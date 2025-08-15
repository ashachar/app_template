# Mock Data Creation Scripts

This folder contains scripts for creating mock data for testing and debugging purposes. **Always check here first before creating new mock data scripts!**

## 🚀 Quick Start

```bash
# Create mock requisitions
python debug_helpers/mock/mock_requisitions.py --test-id BUG_123 --count 3

# Create mock candidates with resumes
python debug_helpers/mock/mock_candidates.py --test-id BUG_123 --count 5

# Create mock applications
python debug_helpers/mock/mock_applications.py --test-id BUG_123 --count 10

# Clean up all mock data
python debug_helpers/mock/mock_requisitions.py --test-id BUG_123 --cleanup-only
```

## 📦 Available Mock Scripts

### 1. **base_mock.py**
Abstract base class providing common functionality for all mock creators:
- Unique prefix generation for easy identification
- Record tracking for cleanup
- Helper methods (generate_mock_email, generate_mock_phone, etc.)
- Standardized create/cleanup interface

### 2. **mock_companies.py**
Creates mock companies:
```bash
python debug_helpers/mock/mock_companies.py --test-id TEST_001 --count 1
```
**Note**: Due to RLS policies, most users cannot create companies directly. The script will use existing companies instead.

### 3. **mock_users.py**
Creates mock users with proper auth entries:
```bash
# Create candidate users
python debug_helpers/mock/mock_users.py --test-id TEST_001 --count 3 --role candidate

# Create recruiter users
python debug_helpers/mock/mock_users.py --test-id TEST_001 --count 2 --role recruiter --company-id <uuid>

# Create candidate with complete resume
python debug_helpers/mock/mock_users.py --test-id TEST_001 --role candidate --with-resume
```

### 4. **mock_candidates.py**
Creates mock candidates with detailed resumes:
```bash
# Create candidates
python debug_helpers/mock/mock_candidates.py --test-id TEST_001 --count 5

# Create candidate with applications
python debug_helpers/mock/mock_candidates.py --test-id TEST_001 --with-applications <req-id-1> <req-id-2>
```

### 5. **mock_requisitions.py**
Creates mock job requisitions:
```bash
# Create requisitions
python debug_helpers/mock/mock_requisitions.py --test-id TEST_001 --count 3

# Output includes automatic verification:
# [MOCK] Created requisition 1: 5dd35ef1-d202-4463-aa3c-d0446c62917d
# [VERIFY] Checking 3 requisitions...
#   ✅ Requisition 5dd35ef1... verified
#      Title: MOCK_TEST_001_b1d8ff_Developer Position 1
#   ✅ Requisition d3df8f52... verified
#      Title: MOCK_TEST_001_b1d8ff_Developer Position 2
# [MOCK] Verified: 3/3 records exist in DB
```

**Important**: The mock requisitions script automatically uses the test recruiter's company by:
1. Running `get_test_recruiter_company.py` to find the company ID
2. Using the company ID from `TEST_RECRUITER_EMAIL` environment variable
3. Falling back to authenticated user's company if available

Make sure `TEST_RECRUITER_EMAIL` is set in your `.env` file!

### 6. **mock_applications.py**
Creates mock applications between candidates and requisitions:
```bash
# Create random applications
python debug_helpers/mock/mock_applications.py --test-id TEST_001 --count 10

# Create full application pipeline for a requisition
python debug_helpers/mock/mock_applications.py --test-id TEST_001 --pipeline <requisition-id>

# Create applications with specific IDs
python debug_helpers/mock/mock_applications.py --test-id TEST_001 \
    --candidates <cand-id-1> <cand-id-2> \
    --requisitions <req-id-1> <req-id-2>
```

### 7. **mock_matches.py**
Creates mock candidate-requisition matches for Hunt page testing:
```bash
# Create matches for specific requisitions
python debug_helpers/mock/mock_matches.py --test-id TEST_001 \
    --requisitions <req-id-1> <req-id-2> \
    --candidates-per-req 5

# This will:
# - Create 5 candidates per requisition with full data
# - Create match records with realistic scores (0.7-0.95)
# - Include matching/missing skills
# - Set best matching titles

# Example output:
# [MOCK] Creating matches for requisition: 5dd35ef1-d202-4463-aa3c-d0446c62917d
#   ✅ Match 1: Score 0.892, 8 matching skills
#   ✅ Match 2: Score 0.845, 7 matching skills
# [VERIFY] Checking 10 matches...
#   ✅ Match a3f2b1c4... verified (score: 0.892)
```

## 🔑 Key Features

### Automatic Verification
**Every mock script automatically verifies that records were created in the database:**
- Queries each created record with SELECT statements
- Shows detailed verification results
- Reports any missing records
- Displays key fields to confirm data integrity

### Unique Prefixes
All mock data is created with unique prefixes like `MOCK_TEST_001_a3f2b1_` to:
- Easily identify test data
- Prevent conflicts with real data
- Enable safe cleanup

### Foreign Key Handling
Scripts handle dependencies automatically:
- Creates parent records first (users before candidates)
- Tracks all created records for proper cleanup
- Respects RLS policies and constraints

### Realistic Data
Mock data includes:
- Proper Hebrew/English names and titles
- Valid Israeli phone numbers
- Realistic resumes with experience and skills
- Appropriate status distributions

## 🧹 Cleanup

Every script supports cleanup mode:
```bash
# Show cleanup queries
python debug_helpers/mock/<script>.py --test-id TEST_001 --cleanup-only

# Execute cleanup (when integrated with runner)
python debug_helpers/mock_cleanup.py --test-id TEST_001
```

## 📝 Best Practices

1. **Always use a unique test ID** for each debugging session
2. **Check existing scripts first** before creating new ones
3. **Track all created records** for proper cleanup
4. **Respect foreign key constraints** - create parent records first
5. **Use realistic data** that matches production patterns
6. **Clean up after testing** to avoid cluttering the database

## 🔧 Creating New Mock Scripts

If you need to create a mock script for a new table:

1. Copy the template structure from existing scripts
2. Inherit from `BaseMockCreator`
3. Implement required methods:
   - `analyze_schema_requirements()`
   - `create_mock_records()`
   - `get_cleanup_queries()`
4. Add the script to this folder
5. Update `__init__.py` with the new class
6. Document it in this README

## 🚨 Important Notes

- **RLS Policies**: Some operations require special permissions (e.g., creating companies)
- **Authentication**: Creating users requires Supabase Auth API access
- **Unique Constraints**: Scripts handle duplicate key errors gracefully
- **Cascade Deletes**: Cleanup queries respect foreign key relationships

## 💡 Integration with Debug Workflow

These mock scripts integrate with the debugging workflow:

```python
# In your debug script
from debug_helpers.mock import MockRequisitionsCreator

# Create mock data
creator = MockRequisitionsCreator("BUG_123")
result = creator.create_all_mock_data(count=5)

# Use the mock data IDs in your tests
requisition_ids = result['created_ids']['requisitions']

# Check verification results
if result['verification']['verified_count'] == len(result['created_ids']):
    print("✅ All mock data verified in database")
else:
    print(f"⚠️  Some records missing: {result['verification']['missing_records']}")

# Clean up when done
creator.cleanup()
```

Remember: **Good mock data leads to reliable tests!**