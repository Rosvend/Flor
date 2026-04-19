# CLAUDE.md — PQRSD Optimization System (Flor)

## Project Context

**Event:** OmegaHack 2026 (Universidad EAFIT, Medellín). 20 effective dev hours. Submission on Devpost by Sun 10:00. Track: **AI Agents & Automation**.

**Allied entity:** Alcaldía de Medellín — **Secretaría de Desarrollo Económico**. The MVP targets this secretariat but must be designed so it generalizes to the other 25 Alcaldía departments and, later, to decentralized municipalities or the private sector.

**Problem domain:** Sustainable management of PQRSD volume in the public sector. Colombia's **Ley 1755 de 2015** (right of petition) mandates a response within **15 business days** for most request types. Current internal process consumes that budget on non-discretionary work (routing, reading, looking up precedents) instead of legal review.

**MVP goal:** Reduce time-to-first-action on a PQRSD by automating the non-discretionary parts — classification, routing, synthesis — so human officials spend their time on legal review and final approval. **Not** reducing the legal deadline itself.

**Channel scope:** the MVP must handle BOTH
- **Official channels** (tracked in Mercurio): web portal, 21 in-person Servicio a la Ciudadanía points, Subsecretaría de Servicio a la Ciudadanía virtual/phone line.
- **Unofficial channels** (today they bypass Mercurio but still generate a legal obligation to respond): personal/institutional email, Alcaldía social media, WhatsApp to directors.

The lack of traceability in unofficial channels is itself part of the problem. Our pipeline normalizes both into the same data lake.

---

## Architecture: Layered Clean Architecture

Strict layered architecture following Clean Architecture principles. Dependencies flow **inward only**. The domain never knows about infrastructure.

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
- Entities: `PQRSD`, `Citizen`, `Department`, `Assignment`, `AuditEntry`, `KnowledgeBaseEntry`
- Value Objects: `PQRSDType`, `Priority`, `Status`, `Radicado`, `Channel`, `ResponseDeadline`
- Domain Services: `PriorityClassifier`, `DeadlineCalculator`, `RoutingEngine`, `DuplicationDetector`
- Ports (interfaces): `PQRSDRepository`, `NotificationPort`, `ClassificationPort`, `SummarizationPort`, `KnowledgeBasePort`
- Zero external dependencies. No imports from other layers.

**Application Layer** (`src/application/`)
- Use Cases: `SubmitPQRSD`, `PreClassifyPQRSD`, `RoutePQRSD`, `SummarizePQRSD`, `DraftResponse`, `ApproveResponse`, `ResolvePQRSD`, `GenerateAlerts`, `AuditPQRSD`
- DTOs: input/output contracts for each use case
- Orchestrates domain objects and calls ports
- No framework code here. No FastAPI, SQLAlchemy, etc.

**Interface Layer** (`src/interfaces/`)
- HTTP controllers (REST endpoints)
- Request/response serialization
- Input validation at the boundary
- Maps external data to DTOs

**Infrastructure Layer** (`src/infrastructure/`)
- Repository implementations (PostgreSQL, Redis, etc.)
- Notification adapters (email, SMS, WhatsApp)
- Ingestion adapters (Meta Graph API, WhatsApp/FLOR webhook)
- AI/NLP classification + summarization adapters
- Knowledge-base adapter (vector store for RAG + Department registry)
- Queue adapters (Celery, RabbitMQ, etc.)
- Implements ports defined in the domain

---

## SOLID Principles — Non-Negotiable

### Single Responsibility
Each class does one thing. `PriorityClassifier` classifies. `RoutingEngine` routes.
A use case that also sends emails and updates the DB is wrong — fix it.

### Open/Closed
New PQRSD types, new departments, new notification channels: extend via new classes.
Do not modify existing use cases or domain services to add new behavior.

### Liskov Substitution
**This applies.** If `UrgentPQRSD` extends `PQRSD`, any code that handles a `PQRSD` must work
correctly with a `UrgentPQRSD` without knowing the difference. If you catch yourself writing
`if isinstance(pqrsd, UrgentPQRSD)` inside a use case or service, you violated LSP — refactor.
Prefer composition over deep inheritance. Use LSP as a design smell detector, not a mandate
for complex hierarchies.

### Interface Segregation
`NotificationPort` should not force every implementor to support every channel.
Split into `EmailPort`, `SMSPort`, `WhatsAppPort` if implementations diverge.

### Dependency Inversion
Use cases depend on port interfaces, not concrete implementations.
Wire dependencies via constructor injection. No `new ConcreteRepository()` inside use cases.

---

## Alcaldía Context — Actors & Existing Process

### Actors
- **Ciudadanía** — writes PQRSDs in natural language via any channel. Ley 1755 forbids requiring a specific format; the citizen may be anonymous.
- **BackOffice / Servicio a la Ciudadanía** — first classification. Determines which of the **26 Alcaldía departments** is competent using the *Matriz Temática*, then routes through Mercurio. Handles misrouted items by redirecting internally.
- **Enlace de la Secretaría de Desarrollo Económico** — second classification inside the secretariat (e.g. routes an employment request to *Subsecretaría de Creación y Fortalecimiento Empresarial*; a credit request to *Banco Distrital*). Monitors deadlines; sends a reminder to the responsible person at **3 business days before the legal limit**.
- **Asesor Jurídico** — legal approval gate. **Every response to a citizen must pass through this office before it's sent.** Immovable. Our summaries and draft responses exist to accelerate this step, not replace it.

### Mercurio
Official Alcaldía filing and tracking system. Our tool **integrates alongside Mercurio**, it does not replace it. We pull from unofficial channels into a shared data lake and can push normalized records into Mercurio.

### Competency boundaries
The Alcaldía is **not** responsible for many issues citizens send to it. The router must detect out-of-scope requests and flag them for redirection rather than assigning them to a department that won't act:
- Waste / recycling → **Emvarias**
- Utilities (water/power/gas) → **EPM**
- Noise, public safety, psychoactive substances → **Policía Nacional**
- Crimes → **Fiscalía General de la Nación**
- Housing / subsidies → **Isvimed**
- Sports venues → **Inder**
- Vehicle tax, departmental health → **Gobernación de Antioquia**

---

## The Three Root Causes (what the MVP must attack)

1. **Misclassification.** Citizens don't know the competencies of the 26 departments; they route by word association. Internal redirects consume days of the 15-day budget.
2. **Critical information buried in long text.** PQRSDs are natural-language documents (up to 7 pages are documented). The actual request is often at the end. Reviewers read the whole thing to find what's being asked.
3. **No precedent registry.** Cases that were already resolved in the past are re-solved from scratch. Prior work is lost.

Every feature below ties back to one or more of these.

---

## MVP Scope — Three Functional Components (OMEGAHACK A / B / C)

The jury evaluates whether the MVP functionally implements **at least one** of these. Aim for A + B, demo C if time allows.

### Component A — Competency Knowledge Base (attacks cause 1 & 3)
- Structured registry of the 26 Alcaldía departments: name, functions, scope, legal competencies, contact.
- Source: public institutional web portals.
- Lives in `domain/entities/Department` + `infrastructure/knowledge_base/` (vector index + structured store).
- Prerequisite for Component B and for the RAG draft-response feature.

### Component B — Automatic Pre-classification (attacks cause 1)
- Input: PQRSD content. Output: `{tipo (P/Q/R/S/D), suggested_department, suggested_subsecretaria?, priority, confidence_score}`.
- For Desarrollo Económico specifically, also propose the internal subsecretariat (e.g. *Creación y Fortalecimiento Empresarial*, *Banco Distrital*).
- Terminology matters: it's **pre-classification**. The tool proposes, the official validates.
- Implements `ClassificationPort`. Adapter lives in `infrastructure/classification/`.
- If `confidence_score < 0.75` → human triage queue, do not auto-assign.

### Component C — Structured Synthesis (attacks cause 2, partially 3)
- Three-layer output per PQRSD:
  1. **Lead / headline** — the concrete request in one sentence.
  2. **Thematic discrimination** — bullets of the distinct topics the document touches.
  3. **Full original text** — kept verbatim as backup.
- Delivery format is flexible: structured email to the enlace, management panel, or both.
- Implements `SummarizationPort`. Adapter lives in `infrastructure/classification/` (same boundary as classification).

---

## Feature Roadmap

Every feature here maps to one of the three components above or is marked as an extension. The underlying user-requested features are preserved; some are rescoped to stay inside the legal constraints.

### F1 — Multi-channel ingestion *(prerequisite for B, C)*
Official + unofficial channels normalized into one data-lake record. See **Channels & Ingestion** below for the Meta + WhatsApp/FLOR specs. Email/portal channels come later.

### F2 — Pre-classification *(Component B)*
Two-stage classification: (a) the P/Q/R/S/D type, (b) competent department among 26, plus optional internal subsecretariat for Desarrollo Económico.

### F3 — Respectfulness / sentiment filter *(extension, scope-reduced)*
**Do not auto-reject disrespectful PQRSDs.** Ley 1755 protects the citizen's right to petition regardless of tone or format — an auto-rejection generates legal exposure. Instead:
- Sentiment model flags the message.
- Flagged messages go to a **moderation queue** for human review.
- The reviewer may redact offensive language and forward, or escalate internally.
The citizen's right to a response is untouched.

### F4 — Duplication / case clustering *(extension, attacks cause 3)*
- Embedding similarity across open + recent resolved PQRSDs.
- Similar PQRSDs link to a parent *case cluster*; cluster priority rises with volume.
- Officials draft one response; it fans out — still with **per-citizen legal-advisor approval** before each send.

### F5 — AI summary + RAG draft response *(Component C + extension)*
- Summary: the three-layer structure from Component C.
- Draft response: generated via RAG over the Component A knowledge base + prior resolved PQRSDs.
- **The draft is for the agent's convenience and is never sent automatically.** The legal-advisor gate is mandatory.

### F6 — Redaction improver (citizen-side) *(extension)*
- Optional "improve my writing" button in the citizen submission UI.
- Purely cosmetic help; the citizen may submit unstructured text and that submission is legally valid.

### F7 — Flor — RAG chatbot *(extension)*
Name disambiguation: **FLOR already exists** as the official Alcaldía Medellín WhatsApp chatbot (Phone number +57 3016044444) and is the ingestion surface for Channel 2 (see below). Our "Flor" layer adds:
- **Citizen-facing Q&A** over the knowledge base — deflects questions that don't need to become PQRSDs.
- **Agent-facing search** — officials query laws, prior resolutions, department competencies without digging through documents. 
Flor should be updated through an upload new document feature where the documents are processed and added to Flor's knowledge base.

### F8 - Computer vision detection for .jpg and .mp4 files
The system should be able to describe what the images uploaded by a citizen are and provide a description for the government agent to read.

---

## Channels & Ingestion

Both channels produce a `Radicado` and timestamp on intake and enter the same pre-classification pipeline.

### Channel 1 — Meta (Facebook & Instagram)
- **Mode:** scheduled sync, every 24 h.
- **Permissions required:** `pages_read_engagement`, `pages_show_list`, `pages_messaging`. Page Access Token per page; no advanced App Review.
- **Endpoints:**
  - Comments: `GET /{page-id}/feed?fields=comments{message,from,created_time}`
  - DMs: `GET /me/conversations?fields=messages{message,from,created_time}`
  - Temporal filter: `since`/`until` on `created_time` (last 24 h window).
- **Pipeline:** every message runs through the classifier. Non-PQRSD content is discarded. PQRSD content is filed personalized when `from.name` is public, anonymous otherwise.
- **`canal` values:** `META_DM` | `META_COMMENT`.

### Channel 2 — WhatsApp via FLOR
- **Mode:** real-time, citizen-initiated via FLOR's "Radicar PQRSD" menu.
- **Fields collected structurally by FLOR:** type (P/Q/R/S/D), citizen name (optional), document number (optional), case description, confirmation.
- **No classifier step needed for `tipo`** — the citizen picked it. We still run department classification (Component B).
- **Personalized vs anonymous:** personalized if name/document present, anonymous otherwise.
- **`canal` value:** `WHATSAPP`.
- FLOR confirms the filing back to the citizen with the generated `radicado`.

### Unified data-lake record
```json
{
  "radicado": "string",
  "timestamp_radicacion": "ISO8601",
  "tipo": "P | Q | R | S | D",
  "canal": "META_DM | META_COMMENT | WHATSAPP | EMAIL | PORTAL | IN_PERSON | PHONE",
  "anonima": true,
  "usuario": {
    "nombre": "string | null",
    "id_meta": "string | null",
    "documento": "string | null",
    "telefono": "string | null"
  },
  "contenido": "string",
  "metadata": {
    "post_id": "string | null",
    "created_time": "ISO8601"
  }
}
```

---

## Domain Model — Core Entities

### `PQRSDType` (P/Q/R/S/D)
Official taxonomy from the PQRSD Alcaldía guide.
```
PETICION   (P) → Formal request for information, service, or access (general or particular interest).
QUEJA      (Q) → Dissatisfaction with the conduct of a public servant or with the quality of attention.
RECLAMO    (R) → Dissatisfaction over a deficient service, delays, or improper charges.
SUGERENCIA (S) → Recommendation to improve a service, function, or objective.
DENUNCIA   (D) → Report of potentially unlawful conduct, corruption, or conflicts of interest.
```

> **Note for domain-layer work:** `backend/src/domain/value_objects/pqrsd_type.py` currently defines `DOUBT`. That is not an official PQRSD type. The first domain commit must rename `DOUBT` → `DENUNCIA` across the code and tests.

### `Priority` (internal operational tier, not a legal SLA)
Used to order internal work *within* the legal deadline. Does **not** override Ley 1755.
```
CRITICAL → health/safety risk, imminent legal deadline, corruption denuncia
HIGH     → repeated complaint, service interruption
MEDIUM   → standard administrative request
LOW      → suggestions, general inquiries
```

### `ResponseDeadline` — legal SLA (Ley 1755 / Ley 1437)
These are the *non-negotiable* deadlines the system must track.
```
Petición general / Queja / Reclamo / Sugerencia                → 15 business days
Denuncia por actos de corrupción                               → 15 business days
PQRSD asociada a trámite                                       → 15 business days
Solicitud de información o copias                              → 10 business days
Solicitud entre entidades públicas                             → 10 business days
Solicitudes del Congreso                                       → 10 business days
Solicitud de conceptos / consultas                             → 30 business days
Solicitudes de oposición                                       → 5  business days
Solicitudes Defensoría del Pueblo                              → 5  business days
```

### `Radicado`
Filing number. Primary public identifier for a PQRSD; used by every actor (citizen, enlace, asesor jurídico, Mercurio). Generated at intake; never reused.

### `Channel`
```
META_DM | META_COMMENT | WHATSAPP | EMAIL | PORTAL | IN_PERSON | PHONE
```

### Entities
- `PQRSD` — aggregate root. Fields: `radicado`, `tipo`, `priority`, `status`, `channel`, `content`, `citizen`, `department_id?`, `subsecretaria_id?`, `deadline`, `created_at`, `resolved_at?`, `cluster_id?`.
- `Citizen` — has `anonima: bool`. May carry `nombre`, `documento`, `telefono`, `id_meta`. None required (legal: no format requirement).
- `Department` — one of 26 Alcaldía departments. Fields defined by Component A (functions, scope, legal competencies, contacts).
- `Assignment` — links a PQRSD to an agent/subsecretariat with timestamps.
- `AuditEntry` — immutable log entry for legal/administrative traceability (Ley 1474).
- `KnowledgeBaseEntry` — a normalized piece of department knowledge or resolved-case precedent, indexed for RAG.

---

## Key Use Cases

```
SubmitPQRSD        → intake from any channel, generate radicado, persist raw record, emit event
PreClassifyPQRSD   → run ClassificationPort; persist proposals; route <0.75 confidence to triage
RoutePQRSD         → apply proposal (after human validation) — assign department / subsecretaría
SummarizePQRSD     → run SummarizationPort; produce 3-layer synthesis for the enlace & asesor
DraftResponse      → RAG over knowledge base + precedents; produce draft for the assigned agent
ApproveResponse    → asesor jurídico sign-off; only then may a response be sent to the citizen
ResolvePQRSD       → record the approved response sent; notify citizen; close ticket
GenerateAlerts     → scheduled job; flags PQRSDs near the legal deadline
AuditPQRSD         → produce traceability log for legal/administrative accountability
```

---

## AI Classification & Summarization Module

`ClassificationPort` and `SummarizationPort` live in the domain. Adapters live in `infrastructure/classification/`. The domain does not know which model or provider is used.

`ClassificationPort.classify(content, channel) → ClassificationResult` returns:
- `tipo`: `PQRSDType` (P / Q / R / S / D)
- `suggested_department`: string ID — one of the 26
- `suggested_subsecretaria`: optional string ID (for Desarrollo Económico scope)
- `priority`: `Priority` (internal tier)
- `confidence_score`: float 0–1

If `confidence_score < 0.75`, the use case must route to the human triage queue instead of auto-assigning.

`SummarizationPort.summarize(pqrsd) → Summary` returns the three-layer structure described in Component C.

---

## Alerts & Escalation Logic

Scheduled jobs (infrastructure layer) call the `GenerateAlerts` use case. The domain defines the rules; infrastructure defines the schedule.

Escalation triggers, measured against the applicable `ResponseDeadline`:
- 50% of SLA elapsed + no department assigned → alert supervisor.
- 80% of SLA elapsed + no draft response → escalate to department head.
- **Legal-deadline reminder:** at **3 business days before the legal deadline** (Alcaldía's current practice), send a reminder to the responsible person with the PQRSD summary attached.
- 100% of SLA elapsed + unresolved → breach flag, mandatory audit log entry, citizen notified of delay (response still owed).

---

## Legal Framework — Non-Negotiable Constraints

The system **cannot**:
- Send any citizen-facing response without **Asesor Jurídico approval** (Ley 1755 de 2015, Ley 1437 de 2011).
- Auto-reject, auto-close, or auto-archive a PQRSD (Ley 1755 — fundamental right of petition; Art. 23 Const.).
- Require a specific format or structure from the citizen (Ley 1755 — no lawyer required, no prescribed format).
- Store, expose, or transmit citizen personal data without compliance with Ley 1581 de 2012 (habeas data).

Reference laws:
- **Ley 1755 de 2015** — right of petition, deadlines, modalities
- **Ley 1437 de 2011** — administrative procedure code (CPACA)
- **Ley 1474 de 2011** — obligation to maintain a PQRSD reception/resolution function
- **Ley 1581 de 2012** — personal data protection
- **Decreto Municipal 883 de 2015** — functions of Secretaría de Gestión Humana y Servicio a la Ciudadanía

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
    ingestion/        ← Meta Graph, WhatsApp/FLOR webhook, email
    classification/   ← ClassificationPort + SummarizationPort adapters
    knowledge_base/   ← vector store + Department registry
    queues/
tests/
  unit/        ← domain and application layers only
  integration/ ← infrastructure adapters
  e2e/         ← full flow from HTTP to DB
```

### Naming Conventions
- Use cases: verb + noun (`SubmitPQRSD`, `SummarizePQRSD`)
- Ports: noun + `Port` (`NotificationPort`, `PQRSDRepository`, `ClassificationPort`, `SummarizationPort`)
- Implementations: noun + technology (`PostgresPQRSDRepository`, `MetaGraphIngestionAdapter`, `OpenAIClassificationAdapter`)
- DTOs: use case name + `Input` / `Output` (`SubmitPQRSDInput`, `SummarizePQRSDOutput`)

### What Not to Do
- Do not put business logic in controllers or repositories.
- Do not import infrastructure modules into domain or application layers.
- Do not use ORM models as domain entities — map them explicitly.
- Do not skip the port interface and inject the concrete adapter directly into use cases.
- Do not write a use case that does more than one business operation.
- Do not send a citizen-facing response from any path that bypasses `ApproveResponse`.

### Testing
- Domain layer: 100% unit test coverage, no mocks needed (pure logic).
- Application layer: unit tests with mocked ports.
- Infrastructure: integration tests against real or containerized services.
- Every use case has at least one happy path and one failure/edge case test.

---

## What This System Is Not

- Not an autonomous responder. Every outbound citizen message passes through the Asesor Jurídico gate.
- Not a replacement for Mercurio. It sits alongside, pulling unofficial channels into the same data model and augmenting official ones.
- Not a chatbot frontend (FLOR is a separate interface/ingestion adapter; our "Flor" RAG layer sits on top).
- Not a document management system (attachments are stored externally, referenced by ID).
- Not a reporting dashboard (that's a read model / separate bounded context).
- Not responsible for the legal content of response templates (those are content owned by the asesor jurídico, not logic).

---

## Hackathon Deliverables (due Sun 10:00)

- **Navigable MVP** demonstrating functional implementation of at least one of Components A / B / C.
- **Public GitHub repo** with a clear README (install + run + sample data).
- **Devpost project description**: problem / relevance / solution / AI role / impact / scalability.
- **Video demo ≤ 3 minutes**: problem context → solution → main features → AI's specific role.
- **Live pitch** during Demos & Pitch session.

Evaluation weights (equal, 20% each): impact & relevance · AI/ML technical implementation · design & UX · reproducibility & documentation · presentation & pitch.
