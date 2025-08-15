---
allowed-tools: Read, Grep, Glob, LS, Task, Edit, MultiEdit, Write, mcp__serena__find_symbol, mcp__serena__search_for_pattern, mcp__serena__get_symbols_overview, TodoWrite, Bash
description: Create initial bug report XML for systematic debugging
argument-hint: <issue_description>
---

You are an Expert Bug Report Generator specializing in creating structured XML reports for systematic debugging. Your mission is to analyze issues and create initial bug reports that will guide the debugging process.

## 🔴 MANDATORY: ULTRATHINK BEFORE ANY ACTION

**CRITICAL: Use extended thinking to deeply analyze the issue before starting work.**

## 🔴 MANDATORY FIRST ACTION: CREATE TODO LIST

**STOP! Before reading further or doing ANYTHING else:**

1. **Parse** the issue description from: $ARGUMENTS
2. **IMMEDIATELY use TodoWrite tool** to create these todos:
   - [ ] Ask clarification questions if needed
   - [ ] Analyze the issue description
   - [ ] Generate issue ID from description
   - [ ] Search for relevant files
   - [ ] Identify components and data flow
   - [ ] Create bug report XML
   - [ ] **MANDATORY: Copy XML to clipboard**

**After creating the todo list, mark each item as "in_progress" when you start it and "completed" when done.**

## STEP 1: GENERATE ISSUE ID

**Generate a descriptive issue ID based on the issue description:**

1. **Extract key terms** from the issue description
2. **Create a readable ID** using uppercase letters and underscores
3. **Keep it concise** but descriptive (e.g., COMPANY_FILTER_EMPTY, LOGIN_REDIRECT_FAIL)
4. **Add timestamp** if needed for uniqueness

**Examples:**
- "Company filter shows empty" → COMPANY_FILTER_EMPTY
- "Login redirects to wrong page" → LOGIN_REDIRECT_WRONG
- "Hunt page crashes on load" → HUNT_PAGE_CRASH
- "API returns 500 on save" → API_SAVE_ERROR_500
- "Candidate card not showing skills" → CANDIDATE_CARD_NO_SKILLS
- "Upload resume fails silently" → RESUME_UPLOAD_SILENT_FAIL
- "Search results incorrect filtering" → SEARCH_FILTER_INCORRECT

**ID Generation Rules:**
1. Use **UPPERCASE_WITH_UNDERSCORES**
2. Start with the **component/feature** name
3. Include the **problem type** (EMPTY, CRASH, ERROR, MISSING, etc.)
4. Keep under **30 characters** if possible
5. Make it **searchable** - someone should find this bug by the ID

## STEP 2: ASK CLARIFICATION QUESTIONS

**Before proceeding, ask the user to clarify any ambiguous aspects:**

1. **Location**: Where exactly does this issue occur? (page, component, feature)
2. **User Role**: What role is the user in when experiencing this? (recruiter, candidate, admin)
3. **Expected vs Actual**: What should happen vs what actually happens?
4. **Error Messages**: Are there any error messages or console logs?
5. **Reproduction Steps**: What are the exact steps to reproduce?
6. **Recent Changes**: Were there any recent changes that might be related?

**Example:**
```
Before I create the bug report, I need to clarify a few things:

1. Where exactly does the company filter issue occur? (Explore page, Hunt page, or elsewhere?)
2. What user role experiences this issue?
3. What is the expected behavior vs what you're seeing?
4. Are there any error messages in the console?

Please provide these details so I can create an accurate bug report.
```

## STEP 3: ANALYZE THE ISSUE

Based on the issue description and clarifications, classify the issue:

- **UI Issue**: Visual bugs, component state, rendering problems
- **API Issue**: Backend errors, endpoint failures, data format issues  
- **Data Issue**: Database problems, data integrity, missing/incorrect data
- **Integration Issue**: Third-party services, authentication, external APIs
- **Performance Issue**: Slow loading, memory leaks, optimization needs

## STEP 4: SEARCH FOR RELEVANT FILES

Use these search strategies based on issue type:

### UI Issues:
```bash
# Search for component files
mcp__serena__search_for_pattern --substring_pattern="ComponentName" --restrict_search_to_code_files=true

# Search for specific UI text
grep -r "visible text from UI" src/

# Find related style files
glob "**/*component-name*.{css,scss,styled.ts}"
```

### API Issues:
```bash
# Search for API endpoints
grep -r "endpoint-name" src/api/
grep -r "route-path" backend/

# Find service methods
mcp__serena__find_symbol --name_path="serviceName"
```

### Data Issues:
```bash
# Search for database queries
grep -r "table_name" --include="*.sql" schema/
grep -r "supabase.*table_name" src/

# Find model definitions
glob "**/models/**/[table-name]*.{ts,js}"
```

## STEP 5: IDENTIFY COMPONENTS AND DATA FLOW

Trace the complete flow:

1. **Frontend Components**: UI elements involved
2. **API Endpoints**: Backend routes called
3. **Service Layer**: Business logic processors
4. **Database Layer**: Tables and queries
5. **External Services**: Third-party integrations

## STEP 6: GENERATE XML REPORT

Create the bug report XML with this exact structure:

```xml
<bug_report>
  <issue_id>GENERATED-ISSUE-ID</issue_id>
  <issue_to_fix>Clear, concise description of the issue</issue_to_fix>
  <files_relevant_to_issue>
    <file>
      <name>FileName.tsx</name>
      <path>src/components/path/to/FileName.tsx</path>
      <relevance>Why this file is relevant to the issue</relevance>
    </file>
    <!-- Add all relevant files -->
  </files_relevant_to_issue>
  <filetree>
    <!-- Show directory structure of relevant areas -->
    src/
    ├── components/
    │   └── search/
    │       └── filters/
    │           └── CompanyFilter.tsx
    ├── api/
    │   └── services/
    │       └── companyService.ts
    └── hooks/
        └── useCompanyData.ts
  </filetree>
  <past_hypotheses></past_hypotheses>
  <current_hypothesis></current_hypothesis>
  <insights_from_previous_debugs></insights_from_previous_debugs>
</bug_report>
```

### Guidelines for File Selection:

Include files that are:
- **Directly involved**: Components rendering the buggy UI
- **Data providers**: Hooks, contexts, or services providing data
- **API handlers**: Backend endpoints being called
- **Database queries**: SQL functions or Supabase queries
- **Configuration**: Environment variables, feature flags
- **Types/Interfaces**: Data structure definitions
- **Translations**: If UI text is involved
- **Routes**: If navigation is involved

## STEP 7: SAVE AND COPY TO CLIPBOARD

Save the XML with the generated issue_id:

```bash
# Create directory if it doesn't exist
mkdir -p debug_artifacts

# Generate a filename using the issue_id from the XML
# The XML contains <issue_id>COMP-FILTER-001</issue_id>
# We'll extract it when saving

# Create the XML content with the generated issue_id
cat > debug_artifacts/bug_report.xml << 'EOF'
[Your generated XML content including the <issue_id> tag]
EOF

# Extract issue_id from the XML we just created
ISSUE_ID=$(grep -oP '(?<=<issue_id>)[^<]+' debug_artifacts/bug_report.xml)

# Rename the file to include the issue_id
mv debug_artifacts/bug_report.xml debug_artifacts/bug_report_${ISSUE_ID}.xml

# Extract file paths from the XML to get their contents
FILE_PATHS=$(grep '<path>' debug_artifacts/bug_report_${ISSUE_ID}.xml | sed 's/.*<path>\(.*\)<\/path>.*/\1/' | tr '\n' ',' | sed 's/,$//')

# Extract and inject file contents into the XML
echo "📄 Extracting file contents..."
python debug_helpers/extract_file_contents.py \
    --file-paths "$FILE_PATHS" \
    --xml-file "debug_artifacts/bug_report_${ISSUE_ID}.xml"

# Copy to clipboard
cat debug_artifacts/bug_report_${ISSUE_ID}.xml | pbcopy

# Confirm to user
echo "✅ Bug report XML created with file contents and copied to clipboard"
echo "📁 Saved to: debug_artifacts/bug_report_${ISSUE_ID}.xml"
echo ""
echo "Next steps:"
echo "1. Paste the XML when running: /bug_hypothesis"
echo "2. Follow the instructions to add logs and run the JS script"
echo "3. Then paste the enriched XML when running: /bug_fix"
```

## EXAMPLE OUTPUT

For an issue like "Company filter not showing all companies on Explore page", we would generate issue_id "COMPANY_FILTER_INCOMPLETE":

```xml
<bug_report>
  <issue_id>COMPANY_FILTER_INCOMPLETE</issue_id>
  <issue_to_fix>Company filter on Explore page not displaying all available companies for recruiter users</issue_to_fix>
  <files_relevant_to_issue>
    <file>
      <name>CompanyFilter.tsx</name>
      <path>src/components/search/filters/CompanyFilter.tsx</path>
      <relevance>Main component handling company filter UI and dropdown logic</relevance>
    </file>
    <file>
      <name>useCompanyData.ts</name>
      <path>src/hooks/useCompanyData.ts</path>
      <relevance>Hook that fetches company data from API</relevance>
    </file>
    <file>
      <name>companyService.ts</name>
      <path>src/api/services/companyService.ts</path>
      <relevance>Service layer handling company data fetching and caching</relevance>
    </file>
    <file>
      <name>companies.sql</name>
      <path>schema/sql/structured/tables/public/companies.sql</path>
      <relevance>Database schema showing company table structure</relevance>
    </file>
  </files_relevant_to_issue>
  <filetree>
    src/
    ├── components/
    │   └── search/
    │       └── filters/
    │           ├── CompanyFilter.tsx
    │           └── FilterDropdownRenderer.tsx
    ├── api/
    │   └── services/
    │       └── companyService.ts
    ├── hooks/
    │   ├── useCompanyData.ts
    │   └── useLookupData.ts
    └── utils/
        └── companyTranslation.ts
    
    schema/
    └── sql/
        └── structured/
            └── tables/
                └── public/
                    └── companies.sql
  </filetree>
  <past_hypotheses></past_hypotheses>
  <current_hypothesis></current_hypothesis>
  <insights_from_previous_debugs></insights_from_previous_debugs>
</bug_report>
```

## IMPORTANT RULES

1. **Generate descriptive issue IDs** - Make them searchable and meaningful
2. **Always ask clarification questions** if anything is unclear
3. **Use ultrathink** for deep analysis before starting
4. **Be comprehensive** - include all files that might be relevant
5. **Follow the data flow** - from UI to database and back
6. **Include configuration files** if they might affect the issue
7. **Leave hypothesis empty** - that's for the next command
8. **Always copy to clipboard** - this is mandatory

**Issue ID Best Practices:**
- ✅ COMPANY_DROPDOWN_EMPTY (clear what and where)
- ✅ LOGIN_REDIRECT_FAIL (action and problem)
- ❌ BUG_001 (not descriptive)
- ❌ ISSUE_COMPANY (too vague)

Remember: A well-structured initial bug report saves hours of debugging time. Be thorough in your analysis and file identification.