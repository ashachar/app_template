-- Example migration with common issues that validation will catch

-- Issue 1: Adding NOT NULL column without default (will fail if table has data)
ALTER TABLE requisitions 
ADD COLUMN priority INTEGER NOT NULL;

-- Issue 2: Missing CASCADE on drop (may fail with dependencies)
ALTER TABLE companies 
DROP COLUMN old_field;

-- Issue 3: Foreign key to non-existent table
ALTER TABLE user_details 
ADD COLUMN category_id INTEGER REFERENCES categories(id);

-- Issue 4: Missing index on foreign key
ALTER TABLE candidates 
ADD COLUMN company_id UUID REFERENCES companies(id);

-- Issue 5: Type mismatch (if user_id is UUID in schema)
ALTER TABLE resumes 
ADD COLUMN user_id INTEGER REFERENCES user_details(id);