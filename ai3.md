Yes. For what you want, I would use a **two-phase Claude workflow**:

1. **Review first — no modifications**
2. **Correct the identified issues — with validation**

This is safer than asking Claude to “review and fix everything” in one instruction. Anthropic's current guidance also recommends explicit, sequential instructions and having Claude verify its work. ([Anthropic Docs][1])

## 1. First ask Claude to perform the review

In your Claude session in VS Code, use:

Act as the senior developer and code reviewer for this project.

Do a comprehensive review of the existing codebase before making any changes.

Important: this phase is REVIEW ONLY. Do not modify, create, delete, rename, or reformat any files.

### Project context

This is a Python SAN/storage monitoring application.

The intended architecture is:

Storage Arrays
↓
Vendor-Specific Collectors
↓
Raw Vendor Data
↓
Normalization
↓
Canonical Data Model
↓
Pandas DataFrames
↓
Validation
↓
PostgreSQL
↓
Grafana

The application connects to multiple enterprise storage arrays, collects operational/configuration/capacity data, normalizes the vendor-specific responses, builds Pandas DataFrames, stores the data in PostgreSQL, and exposes the data to Grafana.

Treat this as infrastructure software where incorrect data can be operationally significant.

### Review objectives

Inspect the codebase and evaluate:

1. Architecture

* Separation between vendor collectors and common application logic
* Separation between collection, normalization, DataFrames, validation, database, and presentation
* Unnecessary coupling
* Circular dependencies
* Duplicated logic
* Areas that should be refactored
* Whether the current architecture will scale as additional storage vendors are added

2. Python implementation

* Error handling
* Exception handling
* Type hints
* Logging
* Configuration handling
* Resource management
* Dependency usage
* Code duplication
* Maintainability
* Testability
* Unnecessary complexity
* Over-engineering

3. Storage/SAN domain correctness
   Pay particular attention to:

* Array identity
* Volume/LUN identity
* Stable identifiers
* Capacity calculations
* Raw capacity
* Usable capacity
* Provisioned capacity
* Allocated capacity
* Used/free capacity
* Thin provisioning
* Snapshot capacity
* Vendor-specific terminology
* Missing API fields
* Empty API responses
* Partial collection failures

Do not assume that different storage vendors use identical semantics for capacity or resource fields.

4. Data pipeline

Trace representative data all the way through:

API
→ Collector
→ Raw data
→ Normalization
→ Canonical model
→ Pandas DataFrame
→ Validation
→ PostgreSQL
→ Grafana

Identify places where data can:

* Be lost
* Be silently changed
* Be incorrectly converted
* Be duplicated
* Be incorrectly typed
* Be silently discarded
* Be incorrectly interpreted
* Become inconsistent between vendors

5. PostgreSQL
   Review:

* Schema design
* Primary keys
* Unique constraints
* Upsert behavior
* Duplicate handling
* Transactions
* Parameterized SQL
* NULL handling
* Timestamp handling
* Connection handling
* Query performance
* Database error handling

6. Grafana
   Identify dependencies between the database implementation and Grafana.

Look for:

* Dashboard queries
* Views
* Expected column names
* Expected metric semantics
* Time-series assumptions
* Queries that could become expensive
* Schema changes that could break dashboards

7. Reliability
   Look for:

* API timeouts
* Authentication failures
* Connection failures
* Rate limiting
* Retry behavior
* Malformed responses
* Unexpected response types
* Missing fields
* Empty responses
* Partial failures
* Database failures
* Silent failures

8. Testing
   Identify:

* Missing tests
* Weak tests
* Untested error paths
* Missing vendor-specific tests
* Missing normalization tests
* Missing DataFrame validation tests
* Missing PostgreSQL tests
* Missing integration tests

9. Security
   Look for:

* Hard-coded credentials
* API keys
* Passwords
* Tokens
* Secrets in logs
* Unsafe configuration
* SQL injection risks
* Sensitive information exposed through exceptions or logging

Do not expose or reproduce secrets if you encounter them.

10. Operational safety

Identify anything that could accidentally cause:

* Data loss
* Incorrect storage reporting
* Destructive storage operations
* Unintended database deletion
* Unintended mass updates
* Unintended removal of records

Pay particular attention to logic where an empty or failed storage API response could accidentally be interpreted as "there are no resources."

### Review rules

* Inspect the actual implementation before making claims.
* Do not speculate about code you have not inspected.
* Distinguish confirmed defects from potential concerns.
* Do not recommend changes merely because you would personally implement the code differently.
* Prioritize correctness, reliability, maintainability, and operational safety.
* Do not modify files during this review.

### Report format

Return the review using these sections:

## Executive Summary

## Critical Issues

Issues that could cause:

* Data loss
* Incorrect storage information
* Security problems
* Major operational impact
* Database corruption or unintended deletion

## High Priority Issues

## Medium Priority Issues

## Low Priority / Maintainability

## Architecture Review

## Storage/SAN Review

## Data Pipeline Review

## PostgreSQL Review

## Grafana Review

## Testing Gaps

## Security Review

## Recommended Remediation Plan

For every finding provide:

* Severity
* File
* Function/Class
* Finding
* Evidence
* Why it matters
* Recommended correction
* Confidence

At the end provide a prioritized remediation plan.

Do not modify any files until I explicitly ask you to begin remediation.

### Why I would do it this way

The critical instruction is:

> **Do not modify any files until I explicitly ask you to begin remediation.**

That gives you a clean review before Claude starts changing things.

---

# 2. Read Claude's review

Don't immediately tell it:

> "Fix everything."

Instead, review its findings.

For example, Claude might find:

```text
CRITICAL
collector/pure_storage.py
collect_volumes()

An empty API response is interpreted as a valid zero-volume result.
The caller subsequently replaces the existing database records.
```

That's the sort of finding you want to understand before allowing an automated fix.

You can then say:

> Fix Critical and High Priority issues. Leave Medium and Low issues unchanged for now.

That gives you much better control.

---

# 3. Tell Claude to start remediation

Once you're satisfied with the review, use a second prompt:

Begin remediation of the issues identified in your previous code review.

Do not perform a general rewrite.

### Remediation rules

1. Address Critical and High Priority findings first.

2. Before modifying each affected area:

* Re-read the relevant implementation.
* Identify all callers and downstream dependencies.
* Confirm that the review finding is actually valid.
* Determine the smallest safe correction.

3. Preserve the existing architecture unless a finding requires an architectural change.

4. Do not:

* Rewrite unrelated code
* Rename unrelated variables/functions
* Reformat unrelated files
* Upgrade dependencies unless required
* Introduce unnecessary abstractions
* Add speculative features
* Change database schema unless necessary
* Change Grafana behavior unless required
* Remove existing functionality merely to simplify the code

5. For every correction:

* Explain the issue briefly.
* Make the smallest appropriate change.
* Add or update tests where appropriate.
* Run the relevant tests.
* Verify that the correction does not introduce regressions.

6. For storage-related code, pay particular attention to the distinction between:

* successful empty results
* failed API requests
* incomplete API responses
* missing fields
* invalid data

Never treat an API/collection failure as a legitimate empty dataset.

7. For database-related changes:

* Preserve transaction integrity.
* Use parameterized SQL.
* Verify upsert/duplicate behavior.
* Check for unintended mass updates/deletes.
* Verify timestamp behavior.
* Consider downstream Grafana dependencies.

8. Do not make destructive operational changes to storage infrastructure.

### Working method

Work incrementally.

For each finding:

REVIEW FINDING
→ VERIFY
→ PLAN CORRECTION
→ MODIFY
→ TEST
→ REVIEW RESULT
→ CONTINUE

After completing each logical group of fixes, report:

* Files changed
* Findings addressed
* Tests run
* Test results
* Remaining concerns

If a finding is incorrect, ambiguous, or cannot be safely corrected without additional information, stop and explain the issue rather than guessing.

Do not claim a test passed unless you actually ran it.

At the end, provide:

## Remediation Summary

## Files Changed

## Findings Fixed

## Findings Not Fixed

## Tests Executed

## Remaining Risks

---

# 4. The workflow I recommend for your project

For your SAN application, I would actually make this your standard Claude workflow:

```text
                  CLAUDE
                    │
                    ▼
             Inspect codebase
                    │
                    ▼
              CODE REVIEW
                    │
                    ▼
             Review findings
                    │
                    ▼
                 YOU
                    │
          approve remediation
                    │
                    ▼
              Claude fixes
                    │
                    ▼
             Run tests/checks
                    │
                    ▼
          Claude reviews fixes
                    │
                    ▼
              Final report
```

This is much better than:

```text
"Review my code and fix everything."
```

The latter gives Claude too much freedom to combine **analysis, design decisions, implementation, and refactoring** into one operation.

Anthropic specifically recommends clear, explicit sequential instructions for complex tasks, and its guidance on agentic coding emphasizes verification and incremental progress. ([Anthropic Docs][1])

## 5. One additional change to your `CLAUDE.md`

I would add a permanent rule along these lines:

```markdown
## Code Review and Remediation

When asked to review the codebase:

1. Review before modifying.
2. Do not modify files during the initial review unless explicitly requested.
3. Identify confirmed defects separately from potential improvements.
4. Prioritize findings by operational impact.
5. For remediation, address Critical and High issues before lower-priority improvements.
6. Verify each finding against the actual implementation before changing it.
7. Make the smallest safe correction.
8. Add or update tests where appropriate.
9. Run relevant tests after changes.
10. Do not claim tests passed unless they were actually executed.
11. Do not perform unrelated refactoring during remediation.
12. For storage-related code, treat empty API results and collection failures as distinct states.
13. For potentially destructive operations, require explicit user confirmation.
```

That means you won't have to repeat the entire methodology every time.

**For your particular application, I would use Claude as both reviewer and implementer, but keep the two phases separate.** Kimi can then be your independent second review after Claude completes the fixes. This gives you:

**Claude review → Claude remediation → Kimi independent review → Claude final corrections → you approve.**

That is a strong workflow for an infrastructure application where correctness of the data pipeline matters as much as the Python code itself.

[1]: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables?utm_source=chatgpt.com "Prompting best practices - Claude Platform Docs"
