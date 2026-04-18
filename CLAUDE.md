# CLAUDE.md — PQRS Optimization System

## Project Context

Hackathon: Urban Administrative Efficiency — PQRS Optimization
Goal: Reduce citizen request response time from 10–15 business days to ≤ 3 business days.
Scope: MVP for a municipal Secretariat (Alcaldía), designed to be replicable across other entities.

---

## Architecture: Layered Clean Architecture

This project uses **strict layered architecture** following Clean Architecture principles.
Dependencies flow **inward only**. The domain never knows about infrastructure.

```
┌─────────────────────────────────────┐
│         Infrastructure Layer        │  ← Frameworks, DB, APIs, queues, email
├─────────────────────────────────────┤
│         Interface Layer             │  ← Controllers, serializers, CLI, HTTP handlers
├─────────────────────────────────────┤
│         Application Layer           │  ← Use cases, orchestration, DTOs
├─────────────────────────────────────┤
│           Domain Layer              │  ← Entities, value objects, domain services, ports
└─────────────────────────────────────┘
```

### Layer Responsibilities

**Domain Layer** (`src/domain/`)
- Entities: `PQRS`, `Citizen`, `Department`, `Assignment`, `SLAPolicy`
- Value Objects: `PQRSType`, `Priority`, `Status`, `TicketId`, `ResponseDeadline`
- Domain Services: `PriorityClassifier`, `DeadlineCalculator`, `RoutingEngine`
- Ports (interfaces): `PQRSRepository`, `NotificationPort`, `ClassificationPort`
- Zero external dependencies. No imports from other layers.

**Application Layer** (`src/application/`)
- Use Cases: `SubmitPQRS`, `RoutePQRS`, `EscalatePQRS`, `ResolvePQRS`, `GenerateAlerts`
- DTOs: input/output contracts for each use case
- Orchestrates domain objects and calls ports
- No framework code here. No Flask, FastAPI, SQLAlchemy, etc.

**Interface Layer** (`src/interfaces/`)
- HTTP controllers (REST endpoints)
- Request/response serialization
- Input validation at the boundary
- Maps external data to DTOs

**Infrastructure Layer** (`src/infrastructure/`)
- Repository implementations (PostgreSQL, Redis, etc.)
- Notification adapters (email, SMS, WhatsApp)
- AI/NLP classification adapters (OpenAI, local model)
- Queue adapters (Celery, RabbitMQ, etc.)
- Implements ports defined in the domain

---

## SOLID Principles — Non-Negotiable

### Single Responsibility
Each class does one thing. `PriorityClassifier` classifies. `RoutingEngine` routes.
A use case that also sends emails and updates the DB is wrong — fix it.

### Open/Closed
New PQRS types, new departments, new notification channels: extend via new classes.
Do not modify existing use cases or domain services to add new behavior.

### Liskov Substitution
**This applies.** If `UrgentPQRS` extends `PQRS`, any code that handles a `PQRS` must work
correctly with a `UrgentPQRS` without knowing the difference. If you catch yourself writing
`if isinstance(pqrs, UrgentPQRS)` inside a use case or service, you violated LSP — refactor.
Prefer composition over deep inheritance. Use LSP as a design smell detector, not a mandate
for complex hierarchies.

### Interface Segregation
`NotificationPort` should not force every implementor to support every channel.
Split into `EmailPort`, `SMSPort`, `PushPort` if implementations diverge.

### Dependency Inversion
Use cases depend on port interfaces, not concrete implementations.
Wire dependencies via constructor injection. No `new ConcreteRepository()` inside use cases.

---

## Domain Model — Core Entities

### PQRS Types (Value Object: `PQRSType`)
```
PETITION   → information or access request
COMPLAINT  → service quality failure
CLAIM      → rights violation or legal demand
SUGGESTION → improvement proposal
```

### Priority Levels (Value Object: `Priority`)
```
CRITICAL   → legal deadline, infrastructure safety, health risk
HIGH       → service interruption, repeated complaint
MEDIUM     → standard administrative request
LOW        → suggestions, general inquiries
```

### SLA Policy
```
CRITICAL  → 24 business hours  (1 day)
HIGH      → 48 business hours  (2 days)
MEDIUM    → 72 business hours  (3 days)  ← this is the target ceiling
LOW       → 72 business hours  (3 days)
```

---

## Key Use Cases

```
SubmitPQRS         → validate input, classify type, assign priority, create ticket, notify citizen
RoutePQRS          → match PQRS to responsible department, assign agent or queue
EscalatePQRS       → trigger when SLA threshold is at 50% and unassigned, or 80% and unresolved
ResolvePQRS        → agent submits resolution, system validates, notifies citizen, closes ticket
GenerateAlerts     → scheduled job; scans all open tickets for SLA breach risk
AuditPQRS          → produce traceability log for legal/administrative accountability
```

---

## Coding Rules

### File Structure
```
src/
  domain/
    entities/
    value_objects/
    services/
    ports/
  application/
    use_cases/
    dtos/
  interfaces/
    http/
    cli/
  infrastructure/
    persistence/
    notifications/
    classification/
    queues/
tests/
  unit/        ← domain and application layers only
  integration/ ← infrastructure adapters
  e2e/         ← full flow from HTTP to DB
```

### Naming Conventions
- Use cases: verb + noun (`SubmitPQRS`, `EscalatePQRS`)
- Ports: noun + `Port` (`NotificationPort`, `PQRSRepository`)
- Implementations: noun + technology (`PostgresPQRSRepository`, `SendGridEmailAdapter`)
- DTOs: use case name + `Input` / `Output` (`SubmitPQRSInput`, `SubmitPQRSOutput`)

### What Not to Do
- Do not put business logic in controllers or repositories
- Do not import infrastructure modules into domain or application layers
- Do not use ORM models as domain entities — map them explicitly
- Do not skip the port interface and inject the concrete adapter directly into use cases
- Do not write a use case that does more than one business operation

### Testing
- Domain layer: 100% unit test coverage, no mocks needed (pure logic)
- Application layer: unit tests with mocked ports
- Infrastructure: integration tests against real or containerized services
- Every use case has at least one happy path and one failure/edge case test

---

## AI Classification Module

The `ClassificationPort` in the domain defines the contract.
The infrastructure adapter calls the AI/NLP service.
The domain does not know what model is being used.

Classification must return:
- `PQRSType` (petition / complaint / claim / suggestion)
- `Priority` (critical / high / medium / low)
- `confidence_score` (float 0–1)
- `suggested_department` (string ID)

If `confidence_score < 0.75`, route to human triage queue instead of auto-assigning.

---

## Alerts & Escalation Logic

Automated jobs (infrastructure layer) call the `GenerateAlerts` and `EscalatePQRS` use cases.
The domain defines the rules. Infrastructure defines the schedule.

Escalation triggers:
- 50% of SLA elapsed + no department assigned → alert supervisor
- 80% of SLA elapsed + no resolution drafted → escalate to department head
- 100% of SLA elapsed + unresolved → breach flag, mandatory audit log entry, citizen notified of delay

---

## What This System Is Not

- Not a chatbot frontend (that's a separate interface adapter)
- Not a document management system (attachments are stored externally, referenced by ID)
- Not a reporting dashboard (that's a read model / separate bounded context)
- Not responsible for legal response templates (those are content, not logic)