# Migration Validation Guide

## Overview

To prevent buggy database migrations, we now have an enhanced validation system:
1. **supabase-data-agent**: Creates migrations with built-in validation checks
2. **migration_validator.py**: Python script for automated validation
3. **migration-validator agent**: Specialized agent for complex validation scenarios

## How It Works

### Built-in Validation in supabase-data-agent

The supabase-data-agent now includes:

1. **Pre-flight checks** before creating migrations
2. **Validation checklist** for common issues
3. **Safe migration templates** to follow
4. **Automated validation** using the Python script

### Validation Workflow

When making schema changes, the supabase-data-agent will:

1. **Load relevant schema files** from `schema/sql/structured/tables/public/`
2. **Check for common issues** using its built-in checklist
3. **Create the migration script** following safe patterns
4. **Run validation script** (`python debug_helpers/migration_validator.py`)
5. **Only execute if validation passes**

### Example Interaction

```
User: "Add a new column called 'priority' to the requisitions table"

AI: I'll help you add a priority column to the requisitions table. Let me use the supabase-data-agent.

[supabase-data-agent loads schema files]
[supabase-data-agent checks existing columns]
[supabase-data-agent creates migration with safe defaults]
[supabase-data-agent runs validation script]
[If validation passes, migration is executed]
```

## Common Validation Checks

The migration-validator will catch:

1. **Missing CASCADE on drops**
   - Suggests adding CASCADE to avoid dependency errors

2. **NOT NULL without defaults**
   - Prevents failures when tables have existing data

3. **Invalid table/column references**
   - Checks against actual schema files

4. **Missing indexes on foreign keys**
   - Suggests performance-improving indexes

5. **Type mismatches**
   - Ensures consistency with existing schema

6. **Unsafe operations**
   - Warns about potential data loss

## Manual Validation

You can also manually validate any migration:

```bash
# Save your migration to a file
cat > my_migration.sql << 'EOF'
ALTER TABLE users 
ADD COLUMN preferences JSONB DEFAULT '{}';
EOF

# Run the validator
python debug_helpers/migration_validator.py my_migration.sql
```

## Benefits

1. **Prevents production errors** - Catches issues before they happen
2. **Saves debugging time** - No more tracing mysterious migration failures
3. **Enforces best practices** - Suggests improvements automatically
4. **Schema awareness** - Always checks against actual schema files

## Schema File Locations

The validator checks these exact paths:
```
schema/sql/structured/tables/public/[table_name].sql
```

Never rely on:
- `schema/sql/schema.sql` (outdated monolithic dump)
- Memory or assumptions about schema

## Example Validation Report

```
=== MIGRATION VALIDATION REPORT ===

Status: FAIL
Errors: 2
Warnings: 1

ERRORS (Must Fix):
  Line 2: Column 'category_id' already exists in table
  Line 3: Referenced table 'categories' not found

WARNINGS (Should Review):
  Line 2: Consider adding index for foreign key column 'category_id'
    Suggestion: CREATE INDEX idx_requisitions_category_id ON requisitions(category_id);

Recommendation: FIX REQUIRED
```

## Quick Tips

1. **Always let the agents handle validation** - Don't bypass the system
2. **Read validation reports carefully** - They explain exactly what's wrong
3. **Fix all ERRORS** - The migration won't work until you do
4. **Consider WARNINGS** - They improve performance and safety
5. **Trust the schema files** - They are the source of truth

Remember: A few seconds of validation saves hours of debugging!