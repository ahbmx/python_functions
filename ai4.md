Yes. In your situation, I would **not ask Claude to “refactor the existing application.”** I would treat the existing application as a **reference implementation** and have Claude reverse-engineer it first, then build a new application from the documented behavior.

That is a materially different workflow.

Claude Code supports a planning workflow where you can have it analyze the project and develop a plan before implementation, which is exactly what I would use here. ([Claude][1])

## The workflow I recommend

```text
                    EXISTING APPLICATION
                            │
                            ▼
                  1. REVERSE ENGINEER
                            │
                            ▼
                 Document how it works
                            │
                            ▼
                    2. DEFINE TARGET
                       ARCHITECTURE
                            │
                            ▼
                    3. REVIEW THE PLAN
                            │
                            ▼
                  4. CREATE NEW PROJECT
                            │
                            ▼
                     5. IMPLEMENT
                            │
                            ▼
                  6. COMPARE BEHAVIOR
                            │
                            ▼
                       7. TEST
```

The important concept is:

> **The old application is the source of behavioral requirements, not the source code for the new architecture.**

That allows Claude to understand what the existing script actually does without carrying its architectural problems into the new application.

---

# Phase 1 — Tell Claude to reverse-engineer the existing application

I would start with Claude in **Plan mode** and give it this prompt.

I want to rebuild this application from scratch.

The existing application is the reference implementation. Do not modify it.

Your first task is to reverse-engineer and document how the existing application actually works.

Do not begin rewriting or refactoring the code.

## Objective

Understand the existing application's:

* Inputs
* Configuration
* Storage-array connections
* Authentication mechanisms
* API calls
* Vendor-specific behavior
* Data extraction
* Data transformations
* Pandas DataFrames
* Validation
* PostgreSQL interactions
* Grafana dependencies
* Error handling
* Logging
* Scheduling/execution flow
* Outputs
* Dependencies
* External systems
* Assumptions
* Known limitations

## Trace the complete data flow

For each major data collection process, trace:

Storage Array
→ API/CLI
→ Collector
→ Raw Response
→ Transformation
→ DataFrame
→ Validation
→ PostgreSQL
→ Grafana

Identify where each transformation occurs.

For important fields, trace the field from the original storage API response all the way to PostgreSQL.

Pay particular attention to:

* Array identity
* Volume/LUN identity
* Capacity
* Used capacity
* Free capacity
* Provisioned capacity
* Allocated capacity
* Pool information
* Snapshot information
* Host/initiator information
* Port information
* Timestamps
* Vendor-specific identifiers

Do not assume that a variable name accurately describes what the value means. Determine the actual behavior from the code.

## Storage vendor analysis

Identify every storage vendor/platform supported by the application.

For each vendor document:

* Vendor
* Array/platform
* Connection mechanism
* API/CLI used
* Authentication
* Endpoints/commands
* Data collected
* Vendor-specific transformations
* Vendor-specific terminology
* Error behavior
* Retry behavior
* Timeout behavior
* Rate limiting considerations
* Unique identifiers

## Database analysis

Determine:

* PostgreSQL schema
* Tables
* Columns
* Data types
* Primary keys
* Foreign keys
* Unique constraints
* Indexes
* Views
* Upsert behavior
* Insert/update behavior
* Delete behavior
* Transaction boundaries
* Connection management

Identify exactly which application code writes to each table.

## Grafana analysis

Search the project for Grafana-related dependencies.

Identify:

* Dashboards
* Queries
* Views
* Tables used by dashboards
* Columns referenced
* Time fields
* Variables
* Expected metric semantics

Do not assume Grafana only depends on obvious database code.

## Execution flow

Determine exactly what happens when the application starts.

Document:

1. Configuration loading
2. Initialization
3. Storage connections
4. Collection order
5. Data transformation
6. Validation
7. Database operations
8. Error handling
9. Cleanup
10. Exit behavior

Identify whether collection is:

* Sequential
* Parallel
* Threaded
* Async
* Scheduled
* Event driven

## Failure behavior

Determine what happens when:

* A storage array is unreachable
* Authentication fails
* An API request times out
* An API returns an error
* An API returns an empty response
* An API returns malformed data
* A required field is missing
* A database connection fails
* A database insert fails
* One vendor fails while other vendors succeed

Pay particular attention to whether an API failure can accidentally be interpreted as a valid empty result.

## Produce documentation

Do not modify the existing application.

Create a proposed documentation set in the response:

### 1. System Overview

Describe the complete application.

### 2. Architecture

Provide a component-level architecture diagram.

### 3. Data Flow

Document the path from storage API to PostgreSQL.

### 4. Vendor Matrix

Create a matrix of supported storage platforms and their collection methods.

### 5. Data Model

Document the important entities and their relationships.

### 6. Database Model

Document tables, keys, relationships, and write behavior.

### 7. Grafana Dependencies

Document database objects consumed by Grafana.

### 8. Execution Flow

Document the runtime sequence.

### 9. Error Handling

Document current behavior and identify weaknesses.

### 10. Behavioral Requirements

Create a list of behaviors that the new application must preserve.

Separate these into:

* Required behavior
* Current implementation details
* Potential bugs
* Unknown behavior
* Assumptions

### 11. Existing Problems

Identify architectural, reliability, maintainability, security, and data-quality problems.

Do not fix them.

### 12. Recommended New Architecture

Only after documenting the existing application, propose a clean architecture for the replacement application.

The replacement architecture should preserve required business behavior while avoiding unnecessary legacy implementation details.

## Important constraints

* Do not modify existing source files.
* Do not delete anything.
* Do not refactor anything.
* Do not implement the replacement yet.
* Do not assume undocumented behavior.
* Clearly identify uncertainty.
* Reference specific files, classes, functions, and configuration when describing behavior.

The goal of this phase is to understand the existing system deeply enough that another developer could rebuild it without needing to read the original implementation.

---

# Phase 2 — Have Claude produce the new architecture

This is where I would be very deliberate.

After Claude finishes the reverse engineering, tell it:

Using the reverse-engineering analysis you just completed, design the architecture for a completely new implementation.

The existing application is the behavioral reference, but its implementation should not be copied blindly.

The new application should be designed around this target architecture:

Storage APIs
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

## Design objectives

The new application should:

* Support multiple storage vendors cleanly.
* Isolate vendor-specific API behavior.
* Use a canonical internal data model.
* Preserve vendor-specific semantics where they cannot safely be normalized.
* Keep collection independent from PostgreSQL.
* Keep Grafana independent from collectors.
* Make each component testable independently.
* Handle partial failures safely.
* Prevent failed collection from being interpreted as an empty dataset.
* Provide clear structured logging.
* Use explicit error handling.
* Use type hints.
* Minimize unnecessary dependencies.
* Be maintainable as additional storage vendors are added.

## Required design output

Provide:

1. Proposed project directory structure
2. Component responsibilities
3. Interfaces between components
4. Canonical data models
5. Collector interface
6. Normalization strategy
7. DataFrame strategy
8. Validation strategy
9. PostgreSQL persistence strategy
10. Error-handling strategy
11. Configuration strategy
12. Logging strategy
13. Testing strategy
14. Grafana/database compatibility strategy
15. Migration/behavioral-equivalence strategy

For every major design decision, explain why it is appropriate based on the behavior of the existing application.

Identify any behavior from the existing application that cannot be safely reproduced without a design decision or additional information.

Do not implement the new application yet.

Produce the architecture and implementation plan first.

---

# Phase 3 — This is where you review Claude's plan

This is the point where **you should stop Claude**.

Don't let it immediately start creating 50 files.

Look at:

* Does it understand what your existing application actually does?
* Did it identify all storage vendors?
* Did it correctly understand the PostgreSQL schema?
* Did it find the Grafana dependencies?
* Did it distinguish collection failure from empty results?
* Does the canonical model make sense?
* Are vendor-specific collectors isolated?
* Is it preserving important existing behavior?
* Is it removing legacy complexity rather than reproducing it?

This is also a good point to send Claude's architecture to **Kimi for an independent review**.

You could ask Kimi:

> Review this proposed replacement architecture against the existing application's documented behavior. Identify missing functionality, incorrect assumptions, dangerous data transformations, and architectural weaknesses. Do not modify anything.

That gives you:

```text
Existing Application
        │
        ▼
     Claude
  Reverse Engineer
        │
        ▼
New Architecture
        │
        ├──────────────► Kimi Review
        │
        ▼
       YOU
   Approve Design
```

---

# Phase 4 — Then let Claude build the new application

Once you're satisfied with the architecture, give Claude a very explicit instruction:

The architecture and implementation plan have been reviewed and approved.

Now create the replacement application as a new implementation.

This is a greenfield implementation.

Do not refactor the existing application into the new architecture.

Do not modify the existing application unless explicitly required to add documentation or establish a controlled comparison.

## Implementation strategy

Build the application incrementally.

Implement in this order:

1. Project structure
2. Configuration
3. Logging
4. Canonical data models
5. Collector interfaces
6. One vendor collector
7. Normalization
8. DataFrame creation
9. Validation
10. PostgreSQL persistence
11. Tests
12. Additional vendor collectors
13. Grafana compatibility
14. End-to-end validation

For each stage:

* Implement the smallest useful component.
* Add tests.
* Run the tests.
* Verify the result.
* Do not proceed if the architecture needs to change.

## Behavioral compatibility

Use the reverse-engineering documentation as the behavioral specification.

Where the old application behavior is intentional, preserve it.

Where the old behavior appears to be a bug, do not reproduce it automatically.

Flag the behavior and explain the difference between:

* Existing behavior
* Intended behavior
* New implementation behavior

## Storage safety

Never allow:

* Failed collection to become an empty dataset
* Invalid API responses to overwrite valid database records
* Unexpected identifiers to be silently accepted
* Unknown capacity semantics to be treated as equivalent
* Database failures to be silently ignored

Do not implement destructive storage operations.

## Code quality

Use:

* Type hints
* Explicit models
* Small testable functions
* Structured logging
* Explicit exceptions
* Clear interfaces
* Dependency injection where appropriate
* Parameterized SQL
* Transaction boundaries
* Tests for failure paths

Avoid:

* Monolithic modules
* Global mutable state
* Vendor-specific logic in shared code
* Copy/paste collectors
* Broad exception handling
* Silent failures
* Unnecessary abstractions

## Validation

After implementation:

* Run unit tests.
* Run integration tests where available.
* Compare representative output against the existing application.
* Verify PostgreSQL records.
* Verify important data fields.
* Verify timestamps.
* Verify capacity calculations.
* Verify vendor-specific identifiers.
* Verify Grafana queries remain compatible.

Do not claim behavioral equivalence without actually testing it.

At the end, provide:

## Implementation Summary

## Files Created

## Files Modified

## Tests Added

## Tests Executed

## Behavioral Differences

## Known Limitations

## Remaining Risks

---

# One important recommendation

I would **not actually put the new application inside the old application's directory and tell Claude to "start over."**

Instead, use something like:

```text
storage-monitoring/
├── legacy/
│   └── existing application
│
├── replacement/
│   └── new application
│
├── docs/
│   ├── legacy-behavior.md
│   ├── architecture.md
│   ├── data-model.md
│   └── database.md
│
└── CLAUDE.md
```

Or, even better, separate projects:

```text
storage-monitoring-legacy/
storage-monitoring-new/
```

This gives Claude a **clean boundary**.

The old application becomes your reference system:

```text
              LEGACY APPLICATION
                     │
                     │ behavior
                     ▼
             DOCUMENTATION
                     │
                     ▼
             NEW ARCHITECTURE
                     │
                     ▼
              NEW APPLICATION
```

That is what I would do for your particular project. You're not asking Claude to make an existing codebase better; you're asking it to **extract the requirements and behavior from an existing system and then engineer a cleaner replacement**.

And because this is SAN/storage software, I would keep the old application available throughout development so you can compare outputs from both systems before retiring it.

[1]: https://code.claude.com/docs/es/changelog?utm_source=chatgpt.com "claude-code/CHANGELOG.md at main · anthropics/claude-code · GitHub"
