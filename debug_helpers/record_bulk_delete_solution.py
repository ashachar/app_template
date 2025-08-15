#!/usr/bin/env python3
"""
Record the bulk delete solution in the failure pattern database
"""
from failure_pattern_db import FailurePatternDB

# Initialize database
db = FailurePatternDB()

# Record the pattern and solution
pattern_id = db.record_pattern(
    pattern_signature={
        'error_type': 'UI',
        'error_message': 'Error toast shown when bulk deleting jobs despite successful deletion',
        'context_keywords': ['bulk', 'delete', 'jobs', 'toast', 'error', 'single', 'selected'],
        'module_hints': ['ui', 'recruiter', 'jobs']
    },
    solution={
        'description': 'Use unified deleteJobs API for all bulk deletions instead of special-casing single job',
        'code_changes': [
            {
                'file_path': 'src/pages/recruiter/Jobs.tsx',
                'description': 'Modified handleDeleteSelectedJobs to always use deleteJobs() API',
                'diff_snippet': '''- if (jobToDelete.id.includes(',')) {
-   const jobIds = jobToDelete.id.split(',');
-   // ... bulk delete logic
- } else {
-   // Single job delete
-   await handleDeleteJob();
- }
+ // Always use bulk delete API, even for single job
+ const jobIds = jobToDelete.id.includes(',') ? jobToDelete.id.split(',') : [jobToDelete.id];
+ // ... unified delete logic using deleteJobs(jobIds)'''
            }
        ],
        'test_cases': ['test_bulk_job_deletion_fix']
    },
    session_id='c0e933dc-d401-47f2-9094-10b01f7b99cc'
)

# Mark the solution as successful
db.record_solution_result(pattern_id, 0, True, 'c0e933dc-d401-47f2-9094-10b01f7b99cc')

print(f" Solution recorded with pattern ID: {pattern_id}")
print(" This solution can help future developers facing similar bulk delete issues!")