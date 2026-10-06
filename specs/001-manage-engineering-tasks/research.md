# Research: Manage Engineering Tasks

## 1. Application shape

**Decision**: One local Python application. A domain module owns every status rule. SQLite stores one workspace. A localhost, server-rendered web UI is the engineer-facing surface and calls that same module.

**Rationale**: The spec is a single-engineer product: list tasks, open one task, and be told when an action is refused. The constitution requires the state machine to be stored, replayable, and free of hidden inference. Putting the rules in one module lets tests prove them without a browser, and the UI cannot invent a second set of transitions. One process matches Principle VIII: the feature is not split across services.

**Alternatives considered**:

- Command-line only. Easier to test, but the success criteria are written as an engineer seeing a list and opening a task. A CLI would still need a second interface later.
- Separate frontend and backend applications. Two deployable parts for one user and one workspace, with no spec need for a public network API.
- Mobile app. The spec never asks for a phone or tablet client.

## 2. Language and runtime

**Decision**: Python 3.12.

**Rationale**: The machine used for this plan has Python 3.12.7, and the Spec Kit scripts in this repository already run on Python. The domain is branching rules and stored records, which Python expresses directly and tests with pytest. No language feature beyond 3.12 is required.

**Alternatives considered**:

- TypeScript with a Node server. A reasonable UI stack, and a second runtime beside the Python tooling already in the repo.
- Go or Rust. Strong for a small binary, and a poorer fit for the fast test-first loop this constitution requires on a rule-heavy domain.

## 3. Storage

**Decision**: One SQLite file per workspace, accessed through the Python standard-library `sqlite3` driver. Foreign keys are enforced. Each engineer command runs in one transaction that commits only when the command is accepted.

**Rationale**: The workspace is one engineer and one file. SQLite gives durable rows for tasks, criteria, status changes, and decisions without a separate database server. A transaction keeps ancestor updates and the task that caused them together, so a refusal leaves the file unchanged. Integer primary keys plus `created_at` give a stable order when the clock returns the same timestamp twice.

**Alternatives considered**:

- JSON or Markdown files. Easy to read, and awkward for "update the ancestor chain or change nothing" without a custom lock protocol.
- PostgreSQL. Appropriate for many users. This feature has no sign-in and no shared workspace.
- An object-relational mapper. Hides the rows the constitution says a reader must be able to inspect. The repository will use explicit SQL.

## 4. Time and replay

**Decision**: The domain accepts a clock. Production uses the system clock. Tests pass a clock that returns scripted times. Every status change, verification, and decision stores the time the clock returned for that command. Ordering of lists uses `created_at` ascending, then `id` ascending. Ordering of history and decisions uses the stored time ascending, then `id` ascending.

**Rationale**: Principle V says the clock must not change a transition unless that time is stored with it. Spec success criterion SC-006 requires two passes of the same actions to produce the same statuses and the same order. It does not require the same wall-clock timestamps. A scripted clock makes the stored times identical in tests as well.

**Alternatives considered**:

- Reading the system clock inside each rule. Two test runs then differ by time even when every decision is the same.
- Leaving time out of the stored record and sorting only by id. The spec requires the history to show when a change happened.

## 5. Who the record names

**Decision**: The workspace is created with one engineer name, taken from configuration, defaulting to `Engineer`. There is no account, password, or session. When a criterion becomes Verified, the current engineer name is copied onto that criterion. Later changes to the configured name do not rewrite older verifications. No command accepts an assistant as the actor.

**Rationale**: Clarification requires the verification record to name the engineer, and the assumptions exclude sign-in. Copying the name at verification time keeps the evidence stable. Omitting every assistant route keeps Principle VI satisfied by having no agent action to hide.

**Alternatives considered**:

- A user table and login. The spec defers sign-in, sharing, and assignment.
- A single shared label with no stored provider. That contradicts the clarification that the record names the engineer.
- Letting the request body supply the provider. A client could then claim another actor. The server copies the configured name.

## 6. Interface style

**Decision**: Server-rendered HTML pages on `127.0.0.1` only, plus a JSON command API that uses the same domain functions. FastAPI serves both. Jinja2 renders the pages. pytest and FastAPI's test client exercise the API. Browser checks are limited to the quickstart paths.

**Rationale**: The pages are the product an engineer uses. The JSON API is the contract tests can call without parsing HTML. One domain function per command means the page and the API cannot disagree. Binding to localhost matches a single local workspace.

**Alternatives considered**:

- A single-page application. A second codebase for forms that submit to the same rules.
- HTML only, with no JSON contract. Harder to assert refusal messages and unchanged records in automated tests.
- A public HTTP service. The spec has one local workspace and no authentication.

## 7. Dependencies

**Decision**: Runtime dependencies are FastAPI, Uvicorn, and Jinja2. Tests use pytest. SQLite comes from the Python standard library. No model API, queue, or authentication library.

**Rationale**: FastAPI gives request parsing and a test client. Uvicorn serves the local process. Jinja2 renders the two pages. Adding a data-access framework or an AI client would widen the surface past the spec.

**Alternatives considered**:

- Flask. Equally capable here. FastAPI's test client and typed request bodies match the command contract more directly.
- Django. An admin, auth, and ORM stack for a product that must not infer status and must not grow accounts in this feature.
- Standard-library HTTP only. Fewer dependencies, and more hand-written parsing before the first domain test can run through the interface.

## 8. Scale and speed targets

**Decision**: Design for one workspace of up to 5,000 tasks, nesting included, on one machine. Each accepted or refused command should complete in under 200 milliseconds at that size. Nesting depth is not capped. Creating a parent link walks ancestors and rejects a cycle.

**Rationale**: The spec's measured outcomes are human times (create a task in under 3 minutes, add a subtask in under 2 minutes). A local command budget of 200 milliseconds keeps the interface from being the limit. A depth cap would contradict the spec, which allows a subtask to have subtasks and rejects only cycles. Five thousand tasks is a planning ceiling, not a spec quota.

**Alternatives considered**:

- A maximum depth of one. Simpler queries, and a direct contradiction of the spec's nesting rule.
- No performance target. Leaves implementers without a check for the ancestor walk on a large workspace.

## Resolved clarifications

No Technical Context item remains open. The stack, storage, test approach, platform, project type, performance target, constraints, and scale are the decisions above.
