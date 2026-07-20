# COMPUTERWISDOM Training Manual v0.2

**Subtitle:** Replay-First Operational Science for Large, Layered Systems  
**Author:** JayWisdom.base.eth / COMPUTERWISDOM  
**Status:** Draft / Governed Curriculum  
**Authority:** `false`  
**Core Rule:** No receipt = no authority.

---

## 0. Purpose

COMPUTERWISDOM is a training discipline for debugging, governing, and restoring complex systems through replayable evidence.

It teaches operators to move from symptoms to receipts, from frustration to classification, and from blocked workflows to restorable constructions.

This manual is not about blaming platforms. It is about proving system behavior.

---

## Module 1 — Observe

Begin with observations, not conclusions.

Example observation ledger:

```text
Console: authenticated
Project: visible
Cloud Shell: no credentialed accounts
Deploy authority: unavailable
```

Observation is evidence. Everything else is inference.

---

## Module 2 — Separate Layers

Every failure belongs to a layer.

```text
Human
Browser
Identity
API
Platform
Infrastructure
Application
```

Never skip layers. A symptom at the application layer may originate in identity, browser session propagation, IAM, or platform control-plane behavior.

---

## Module 3 — Replay

A failure is not operationally useful until it can be replayed.

A replay must include:

- actor
- environment
- command or UI action
- input
- output
- timestamp
- expected result
- actual result
- classification

Replay turns memory into evidence.

---

## Module 4 — Resistance

Large systems resist change for different reasons.

Resistance classes:

- **Policy resistance** — refusal by design
- **Bug resistance** — refusal by accident
- **Constraint resistance** — refusal due to architecture, physics, quota, latency, region, or dependency
- **Unsupported resistance** — refusal because the workflow is outside the platform contract

The operator’s job is not to assume the class. The operator’s job is to prove it.

---

## Module 5 — Recursive Learning

Every blocked workflow becomes training material.

```text
Problem
Observation
Receipt
Replay
Verification
Manual
Protocol
Automation
```

Nothing is wasted if the failure becomes replayable.

---

## Module 6 — Receipt Engineering

A receipt is a structured witness artifact.

Minimum fields:

```text
receipt_id
timestamp
actor
environment
action
input_hash
output_hash
status
classification
replay_instructions
authority:false
```

A receipt does not prove truth. It proves what was observed under stated conditions.

---

## Module 7 — Restore

Good operators do not only find failures. They build restorable paths.

A restoration path must answer:

- What broke?
- What state is known-good?
- What is the minimum recovery step?
- What evidence proves recovery?
- What gate prevents premature deployment?

---

## Module 8 — COMPUTERWISDOM Doctrine

COMPUTERWISDOM favors:

- replay over memory
- receipts over screenshots
- protocols over opinions
- evidence over narrative
- restoration over blame
- gates over vibes

The goal is not to defeat large platforms. The goal is to remain operational when large platforms behave ambiguously.

---

# Module 9 — Adversarial Replay

Adversarial Replay is the discipline of constructing minimal, isolating, replayable experiments that force a system to reveal whether a failure is caused by policy, bug, constraint, or unsupported behavior.

It is the scientific method applied to distributed systems under uncertainty.

---

## 9.1 Purpose

Large systems rarely tell you the truth directly. They reveal symptoms.

Replay converts symptoms into evidence. Adversarial replay converts evidence into classification.

The goal is not merely to fix a bug. The goal is to prove what category of resistance you are dealing with.

Categories:

- **Policy resistance** — the system refuses by design
- **Bug resistance** — the system refuses by accident
- **Constraint resistance** — the system refuses because of architecture, quota, region, identity propagation, or other structural constraints
- **Unsupported resistance** — the system refuses because the request is outside its contract

Adversarial replay distinguishes these without insider access.

---

## 9.2 Core Method

Adversarial Replay follows a strict reduction protocol.

### 1. Isolate the failing surface

Strip the scenario to the smallest possible action that still fails.

### 2. Remove narrative

Do not assign intent. Preserve observations.

Bad:

```text
The platform hates mobile developers.
```

Good:

```text
gcloud auth list returned: No credentialed accounts.
```

### 3. Construct the minimal failing case

One command. One actor. One resource. One permission. One timestamp.

### 4. Replay across membranes

Change exactly one variable at a time:

- same actor, different resource
- same resource, different actor
- same action, different region
- same request, different time
- same payload, different API version
- same workflow, different execution rail

### 5. Observe resistance posture

The pattern of failure reveals the resistance class.

### 6. Produce the adversarial receipt

A formal artifact containing:

- minimal failing case
- replay matrix
- resistance classification
- unknowns
- recommended next replay

This is the unit test for reality.

---

## 9.3 Canonical Example: Cloud Identity Handoff

Observed condition:

```text
Google Cloud Console: authenticated
Project visible: jaywisdom-boardroom
Cloud Shell: no credentialed accounts
```

Minimal failing command:

```bash
gcloud auth list
```

Observed output:

```text
No credentialed accounts.
```

Gate rule:

```text
No credentialed account = no deploy authority.
```

Inference:

```text
Console authentication does not imply Cloud Shell VM authentication.
```

Unknown:

```text
Root cause may be browser/session propagation, Cloud Shell VM credential injection, gcloud config corruption, IAM/account issue, or platform incident.
```

---

## 9.4 Replay Matrix Specification

A replay matrix records controlled variations.

| Variable | Baseline | Variant | Expected Result | Actual Result | Classification Signal |
|---|---|---|---|---|---|
| Actor | same Google account | different account | auth differs | TBD | IAM/account signal |
| Resource | same project | different project | project scope differs | TBD | IAM/project signal |
| Execution rail | Cloud Shell | GitHub Actions WIF | auth differs | TBD | browser/Cloud Shell signal |
| Browser | iOS Safari | desktop browser | auth differs | TBD | browser/session signal |
| Command | `gcloud auth list` | metadata token check | failure repeats | TBD | credential injection signal |

Matrix rule:

```text
Only one variable changes per replay.
```

---

## 9.5 Adversarial Receipt Schema

```json
{
  "schema": "computerwisdom.adversarial_receipt.v0.1",
  "receipt_id": "sha256:<hash>",
  "timestamp_utc": "<iso8601>",
  "actor": "<identity or pseudonymous handle>",
  "system": "<platform/system under test>",
  "resource": "<project/repo/service/resource>",
  "minimal_case": {
    "command_or_action": "<exact command or UI action>",
    "input_hash": "sha256:<hash>",
    "expected_output": "<expected>",
    "actual_output_hash": "sha256:<hash>"
  },
  "replay_matrix_ref": "<path or receipt id>",
  "resistance_classification": "POLICY | BUG | CONSTRAINT | UNSUPPORTED | UNKNOWN",
  "authority": false,
  "unknowns": [],
  "recommended_next_replay": "<next controlled variation>"
}
```

---

## 9.6 Resistance Classification Protocol

Classify only after replay evidence exists.

### POLICY

Use when refusal is consistent, documented, and expected.

Evidence pattern:

```text
same actor + same request + documented denial = repeated refusal
```

### BUG

Use when behavior contradicts documentation or varies unexpectedly without controlled cause.

Evidence pattern:

```text
same actor + same request + same conditions = inconsistent result
```

### CONSTRAINT

Use when behavior is explainable by architecture, quota, region, timing, device, or control-plane limitation.

Evidence pattern:

```text
failure changes when one environmental constraint changes
```

### UNSUPPORTED

Use when the workflow falls outside the platform contract.

Evidence pattern:

```text
vendor docs or support boundary says workflow is not supported
```

### UNKNOWN

Use when evidence is insufficient.

Unknown is a valid state. Fake certainty is not.

---

## 9.7 Anti-Patterns

- **Narrative debugging** — assigning intent instead of evidence
- **Shotgun reconfiguration** — changing many variables at once
- **Heisenbug folklore** — preserving superstition instead of replay conditions
- **Non-minimal reproduction** — requiring the whole system to be rebuilt to observe one failure
- **Premature deployment** — creating resources before the evidence gate passes

---

## 9.8 Exercises

### Exercise A — Auth Chain Failure

Given:

```text
Console authenticated
Cloud Shell unauthenticated
```

Build:

- one minimal failing case
- one replay matrix
- one adversarial receipt
- one restoration path

### Exercise B — IAM Denial

Given:

```text
Permission denied
```

Determine whether the cause is actor, resource, role, organization policy, or API surface.

### Exercise C — Agent Tool Failure

Given:

```text
AI agent claims tool call succeeded, but no external state changed.
```

Produce a receipt that separates model narrative from system evidence.

---

## 9.9 v0.2 Deliverables

COMPUTERWISDOM v0.2 includes:

- Module 9 — Adversarial Replay
- Adversarial Receipt Schema
- Replay Matrix Specification
- Resistance Classification Protocol
- Minimal Failing Case Construction Guide
- Adversarial Replay Exercises

---

## Final Gate

```text
No receipt = no authority
No credentialed account = no deploy authority
No plan witness = no deploy authority
No replay = no classification
```

**End of COMPUTERWISDOM Training Manual v0.2.**
