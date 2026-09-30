For your project, I would **not** simply ask Kimi, “Review my code.” Give Kimi a specific role and review criteria. Since Kimi is useful for large-context analysis, use it primarily as an **independent reviewer**, not as another implementation agent.

### Recommended prompt

Paste this into Kimi in VS Code:

```text
Act as a senior Python and SAN storage software reviewer.

Review this project as an independent code review. Do NOT modify any files.

Project architecture:

Storage arrays
    ↓
Vendor-specific collectors
    ↓
Raw vendor data
    ↓
Normalization
    ↓
Canonical data model
    ↓
Pandas DataFrames
    ↓
Validation
    ↓
PostgreSQL
    ↓
Grafana

Review the entire relevant codebase before reaching conclusions.

Focus on:

1. Architecture
- Are responsibilities correctly separated?
- Are vendor-specific details isolated from the common data model?
- Are there inappropriate dependencies between collectors, Pandas, PostgreSQL, and Grafana?
- Identify architectural coupling and unnecessary complexity.

2. Python quality
- Error handling
- Exception handling
- Type hints
- Logging
- Resource management
- Configuration management
- Dependency usage
- Code duplication
- Maintainability
- Testability

3. Storage/SAN domain correctness
- Storage identifiers
- Volume/LUN identity
- Capacity calculations
- Raw vs usable vs allocated vs provisioned vs used/free capacity
- Vendor-specific semantics
- Handling of missing or unexpected API data
- Partial collection failures
- Timeouts and API failures
- Whether stable identifiers are used instead of transient OS/device names

Do not assume that different storage vendors use the same terminology or capacity semantics.

4. Data pipeline
Trace the data through:

API → collector → normalization → canonical model → DataFrame → validation → PostgreSQL.

Identify where data can be lost, corrupted, incorrectly transformed, duplicated, or silently accepted.

5. PostgreSQL
Review:
- Schema assumptions
- Primary/unique keys
- Upsert behavior
- Transactions
- Parameterized SQL
- NULL handling
- Timestamp handling
- Duplicate handling
- Performance
- Connection management

6. Grafana dependencies
Identify whether database/schema changes could break dashboards, queries, views, or expected metric semantics.

7. Reliability
Look for:
- Silent failures
- Broad exception handling
- Retry problems
- Partial failures
- Empty API responses
- Malformed API responses
- Authentication failures
- Timeouts
- Rate limiting
- Database failures

8. Testing
Identify:
- Missing tests
- Weak tests
- Untested error paths
- Missing vendor/API mocks
- Missing data-validation tests
- Missing database tests

9. Security
Look for:
- Credentials or secrets in source
- Unsafe logging
- Hard-coded connection information
- SQL injection risks
- Unsafe handling of API responses
- Excessive permissions or unsafe operations

10. Operational safety
Because this is SAN/storage infrastructure software, identify anything that could accidentally cause destructive or disruptive storage operations.

Do not propose destructive changes without explicitly identifying the risk.

Review rules:

- Do not modify files.
- Do not rewrite the application.
- Do not make changes just for style preferences.
- Do not invent vendor behavior.
- Distinguish confirmed problems from potential concerns.
- Reference the specific file and relevant function/class for every finding.
- Explain why each finding matters.
- Prioritize findings by severity.

Return the review in this format:

## Executive Summary

## Critical Findings
Issues that could cause data loss, corruption, incorrect storage information, security problems, or major operational impact.

## High Priority Findings

## Medium Priority Findings

## Low Priority / Maintainability

## Architecture Review

## Data Pipeline Review

## Storage/SAN Domain Review

## PostgreSQL Review

## Testing Gaps

## Security Review

## Recommended Remediation Plan

For each finding use:

- Severity:
- File:
- Function/Class:
- Finding:
- Why it matters:
- Evidence:
- Recommended approach:
- Confidence:

Do not implement any recommendations. This is a review only.
```

### Why this works better

For your setup, I would divide the AI responsibilities like this:

```text
                    YOU
                     │
                     ▼
              Requirements
                     │
                     ▼
                  CLAUDE
          Primary implementation
                     │
                     ▼
                  KIMI
          Independent code review
                     │
                     ▼
                   YOU
          Final technical decision
```

The important part is **independent review**.

Don't give Kimi a prompt like:

> "Claude wrote this. Tell me if Claude is right."

That creates anchoring bias. Instead, give Kimi the architecture and requirements and ask it to form its **own assessment from the code**.

### An even better workflow

For a significant change, use three separate passes.

**1. Claude — implement**

```text
Implement this change according to the project architecture and CLAUDE.md.

Before modifying anything:
- inspect the relevant code
- identify affected components
- identify downstream dependencies
- explain your implementation plan

Then implement the smallest appropriate change and run the relevant tests.
```

**2. Kimi — review**

Use the detailed review prompt above, with:

> **Do not modify files.**

**3. Claude — respond to the review**

Give Claude Kimi's findings and say:

```text
Kimi independently reviewed the code and identified the findings below.

Do not blindly accept them.

For each finding:
1. Verify whether it is actually present.
2. Explain whether the finding is valid or not.
3. If valid, determine the appropriate remediation.
4. Do not make unrelated changes.
5. Implement only the approved/necessary fixes.
6. Run the relevant tests afterward.

Do not modify files until you have summarized which findings you intend to address.
```

This creates a useful **implement → independently review → remediate** cycle.

For your storage application, I would make Kimi particularly aggressive about **data semantics and pipeline integrity**. A Python application can pass every unit test while still incorrectly reporting a vendor's `allocated`, `used`, `provisioned`, or `usable` capacity to PostgreSQL. That's exactly the type of cross-layer problem an independent large-context review should look for.
