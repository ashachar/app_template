#!/usr/bin/env python3
"""
Migration Validator - Validates SQL migration scripts against actual schema
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    level: ValidationLevel
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class MigrationValidator:
    def __init__(self):
        # Find the project root (where schema directory is)
        current_path = Path.cwd()
        if current_path.name == 'debug_helpers':
            # We're in debug_helpers, go up one level
            project_root = current_path.parent
        else:
            # Assume we're at project root
            project_root = current_path
            
        self.schema_path = project_root / "schema/sql/structured/tables/public"
        self.schema_cache = {}
        self.issues = []
        
    def load_table_schema(self, table_name: str) -> Optional[str]:
        """Load and cache table schema from structured files"""
        if table_name in self.schema_cache:
            return self.schema_cache[table_name]
            
        schema_file = self.schema_path / f"{table_name}.sql"
        if schema_file.exists():
            content = schema_file.read_text()
            self.schema_cache[table_name] = content
            return content
        return None
        
    def extract_table_info(self, schema_content: str) -> Dict:
        """Extract column names, types, and constraints from schema"""
        info = {
            "columns": {},
            "constraints": [],
            "indexes": []
        }
        
        # Remove comments
        lines = []
        for line in schema_content.split('\n'):
            if '--' in line:
                line = line[:line.index('--')]
            lines.append(line)
        clean_content = '\n'.join(lines)
        
        # Find CREATE TABLE statement
        create_match = re.search(r'CREATE TABLE\s+(?:public\.)?(\w+)\s*\((.*?)\);', 
                                clean_content, re.IGNORECASE | re.DOTALL)
        if not create_match:
            return info
            
        table_body = create_match.group(2)
        
        # Parse columns - more flexible pattern
        for line in table_body.split(','):
            line = line.strip()
            if not line:
                continue
                
            # Skip constraints for now
            if any(keyword in line.upper() for keyword in ['CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'CHECK']):
                continue
                
            # Match column definition
            col_match = re.match(r'(\w+)\s+(.+?)(?:\s+(NOT\s+NULL|NULL|DEFAULT.*))?$', line, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1).lower()
                col_type = col_match.group(2).strip()
                constraints = col_match.group(3) or ""
                
                info["columns"][col_name] = {
                    "type": col_type,
                    "nullable": "NOT NULL" not in constraints.upper(),
                    "has_default": "DEFAULT" in constraints.upper()
                }
            
        # Extract foreign keys - both inline and constraint style
        # Inline style: column_name type REFERENCES table(column)
        inline_fk_pattern = r'(\w+)\s+[^,]+\s+REFERENCES\s+(?:public\.)?(\w+)\s*\((\w+)\)'
        for match in re.finditer(inline_fk_pattern, table_body, re.IGNORECASE):
            info["constraints"].append({
                "type": "foreign_key",
                "column": match.group(1).lower(),
                "ref_table": match.group(2).lower(),
                "ref_column": match.group(3).lower()
            })
            
        # Constraint style: FOREIGN KEY (column) REFERENCES table(column)
        fk_pattern = r'FOREIGN KEY\s*\((\w+)\)\s*REFERENCES\s+(?:public\.)?(\w+)\s*\((\w+)\)'
        for match in re.finditer(fk_pattern, table_body, re.IGNORECASE):
            info["constraints"].append({
                "type": "foreign_key",
                "column": match.group(1).lower(),
                "ref_table": match.group(2).lower(),
                "ref_column": match.group(3).lower()
            })
            
        return info
        
    def validate_migration(self, migration_sql: str) -> Tuple[bool, List[ValidationIssue]]:
        """Main validation method"""
        self.issues = []
        
        # Split into statements (handle multi-line statements)
        statements = []
        current_statement = []
        
        for line in migration_sql.split('\n'):
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue
            current_statement.append(line)
            if ';' in line:
                statements.append('\n'.join(current_statement))
                current_statement = []
                
        if current_statement:
            statements.append('\n'.join(current_statement))
            
        # Process each statement
        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
                
            # Get line number for error reporting
            first_line = statement.split('\n')[0]
            line_num = migration_sql.split('\n').index(first_line) + 1 if first_line in migration_sql else 1
                
            # Check different operation types
            if re.match(r'ALTER\s+TABLE', statement, re.IGNORECASE):
                self._validate_alter_table(statement, line_num, [])
            elif re.match(r'CREATE\s+TABLE', statement, re.IGNORECASE):
                self._validate_create_table(statement, line_num, [])
            elif re.match(r'DROP\s+TABLE', statement, re.IGNORECASE):
                self._validate_drop_table(statement, line_num)
            elif re.match(r'INSERT\s+INTO', statement, re.IGNORECASE):
                self._validate_insert(statement, line_num)
                
        # Determine if migration is safe
        has_errors = any(issue.level == ValidationLevel.ERROR for issue in self.issues)
        return not has_errors, self.issues
        
    def _validate_alter_table(self, line: str, line_num: int, remaining_lines: List[str]):
        """Validate ALTER TABLE statements"""
        # Extract table name
        table_match = re.match(r'ALTER\s+TABLE\s+(\w+)', line, re.IGNORECASE)
        if not table_match:
            return
            
        table_name = table_match.group(1).lower()
        schema = self.load_table_schema(table_name)
        
        if not schema:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Table '{table_name}' not found in schema",
                line_number=line_num,
                suggestion=f"Verify table name or check schema/sql/structured/tables/public/{table_name}.sql"
            ))
            return
            
        table_info = self.extract_table_info(schema)
        
        # Check ADD COLUMN
        if 'ADD COLUMN' in line.upper():
            self._validate_add_column(line, line_num, table_info, table_name)
            
        # Check DROP COLUMN  
        if 'DROP COLUMN' in line.upper():
            self._validate_drop_column(line, line_num, table_info)
            
        # Check ADD CONSTRAINT
        if 'ADD CONSTRAINT' in line.upper():
            self._validate_add_constraint(line, line_num, table_info)
            
    def _validate_add_column(self, line: str, line_num: int, table_info: Dict, table_name: str):
        """Validate ADD COLUMN operations"""
        # More flexible pattern for ADD COLUMN
        col_match = re.search(r'ADD\s+COLUMN\s+(\w+)\s+(.+?)(?:;|$)', line, re.IGNORECASE | re.DOTALL)
        if not col_match:
            return
            
        col_name = col_match.group(1).lower()
        col_definition = col_match.group(2).strip()
        
        # Check if column already exists
        if col_name in table_info["columns"]:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Column '{col_name}' already exists in table",
                line_number=line_num
            ))
            return
            
        # Check NOT NULL without DEFAULT
        if re.search(r'\bNOT\s+NULL\b', col_definition, re.IGNORECASE) and not re.search(r'\bDEFAULT\b', col_definition, re.IGNORECASE):
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Adding NOT NULL column '{col_name}' without DEFAULT will fail if table has data",
                line_number=line_num,
                suggestion=f"Add a DEFAULT value: ADD COLUMN {col_name} {col_definition} DEFAULT <value>"
            ))
            
        # Check foreign key references
        fk_match = re.search(r'REFERENCES\s+(\w+)\s*\((\w+)\)', col_definition, re.IGNORECASE)
        if fk_match:
            ref_table = fk_match.group(1).lower()
            ref_column = fk_match.group(2).lower()
            
            # Check if referenced table exists
            ref_schema = self.load_table_schema(ref_table)
            if not ref_schema:
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Referenced table '{ref_table}' not found",
                    line_number=line_num,
                    suggestion=f"Verify the referenced table name"
                ))
            else:
                # Suggest index for foreign key
                self.issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message=f"Consider adding index for foreign key column '{col_name}'",
                    line_number=line_num,
                    suggestion=f"CREATE INDEX idx_{table_name}_{col_name} ON {table_name}({col_name});"
                ))
                
    def _validate_drop_column(self, line: str, line_num: int, table_info: Dict):
        """Validate DROP COLUMN operations"""
        col_match = re.search(r'DROP\s+COLUMN\s+(\w+)', line, re.IGNORECASE)
        if not col_match:
            return
            
        col_name = col_match.group(1).lower()
        
        # Always warn about CASCADE for safety
        if "CASCADE" not in line.upper():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message=f"DROP COLUMN without CASCADE may fail if there are dependent objects",
                line_number=line_num,
                suggestion=f"Consider using: DROP COLUMN {col_name} CASCADE;"
            ))
            
        # Check if column exists (if we have table info)
        if table_info.get("columns") and col_name not in table_info["columns"]:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Column '{col_name}' does not exist in table",
                line_number=line_num
            ))
            
    def _validate_add_constraint(self, line: str, line_num: int, table_info: Dict):
        """Validate ADD CONSTRAINT operations"""
        # Check for foreign key constraints
        if "FOREIGN KEY" in line.upper():
            fk_match = re.search(r'FOREIGN\s+KEY\s*\((\w+)\)\s*REFERENCES\s+(\w+)\s*\((\w+)\)', 
                               line, re.IGNORECASE)
            if fk_match:
                col_name = fk_match.group(1).lower()
                ref_table = fk_match.group(2).lower()
                
                # Check if column exists
                if col_name not in table_info["columns"]:
                    self.issues.append(ValidationIssue(
                        level=ValidationLevel.ERROR,
                        message=f"Column '{col_name}' does not exist for foreign key",
                        line_number=line_num
                    ))
                    
    def _validate_create_table(self, line: str, line_num: int, remaining_lines: List[str]):
        """Validate CREATE TABLE statements"""
        table_match = re.match(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', line, re.IGNORECASE)
        if not table_match:
            return
            
        table_name = table_match.group(1).lower()
        schema = self.load_table_schema(table_name)
        
        if schema and "IF NOT EXISTS" not in line.upper():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Table '{table_name}' already exists",
                line_number=line_num,
                suggestion="Use CREATE TABLE IF NOT EXISTS"
            ))
            
    def _validate_drop_table(self, line: str, line_num: int):
        """Validate DROP TABLE statements"""
        table_match = re.match(r'DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(\w+)', line, re.IGNORECASE)
        if not table_match:
            return
            
        table_name = table_match.group(1).lower()
        schema = self.load_table_schema(table_name)
        
        if not schema and "IF EXISTS" not in line.upper():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Table '{table_name}' does not exist",
                line_number=line_num,
                suggestion="Use DROP TABLE IF EXISTS"
            ))
            
        if "CASCADE" not in line.upper():
            self.issues.append(ValidationIssue(
                level=ValidationLevel.WARNING,
                message="DROP TABLE without CASCADE may fail if there are foreign key references",
                line_number=line_num,
                suggestion=f"Consider using: DROP TABLE {table_name} CASCADE;"
            ))
            
    def _validate_insert(self, line: str, line_num: int):
        """Validate INSERT statements"""
        table_match = re.match(r'INSERT\s+INTO\s+(\w+)', line, re.IGNORECASE)
        if not table_match:
            return
            
        table_name = table_match.group(1).lower()
        schema = self.load_table_schema(table_name)
        
        if not schema:
            self.issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message=f"Table '{table_name}' not found for INSERT",
                line_number=line_num
            ))
            
    def generate_report(self, migration_sql: str) -> str:
        """Generate a formatted validation report"""
        is_safe, issues = self.validate_migration(migration_sql)
        
        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        warnings = [i for i in issues if i.level == ValidationLevel.WARNING]
        infos = [i for i in issues if i.level == ValidationLevel.INFO]
        
        report = []
        report.append("=== MIGRATION VALIDATION REPORT ===\n")
        report.append(f"Status: {'PASS' if is_safe else 'FAIL'}")
        report.append(f"Errors: {len(errors)}")
        report.append(f"Warnings: {len(warnings)}")
        report.append(f"Info: {len(infos)}\n")
        
        if errors:
            report.append("ERRORS (Must Fix):")
            for err in errors:
                report.append(f"  Line {err.line_number}: {err.message}")
                if err.suggestion:
                    report.append(f"    Suggestion: {err.suggestion}")
                    
        if warnings:
            report.append("\nWARNINGS (Should Review):")
            for warn in warnings:
                report.append(f"  Line {warn.line_number}: {warn.message}")
                if warn.suggestion:
                    report.append(f"    Suggestion: {warn.suggestion}")
                    
        report.append(f"\nRecommendation: {'SAFE TO RUN' if is_safe else 'FIX REQUIRED'}")
        
        return "\n".join(report)


def main():
    """CLI interface for the validator"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration_validator.py <migration_file.sql>")
        sys.exit(1)
        
    migration_file = sys.argv[1]
    
    if not os.path.exists(migration_file):
        print(f"Error: Migration file '{migration_file}' not found")
        sys.exit(1)
        
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
        
    validator = MigrationValidator()
    report = validator.generate_report(migration_sql)
    print(report)
    
    # Exit with appropriate code
    is_safe, _ = validator.validate_migration(migration_sql)
    sys.exit(0 if is_safe else 1)


if __name__ == "__main__":
    main()