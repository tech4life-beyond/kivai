# KIVAI v1.0 Platform Scope

**Platform:** Kivai  
**Focus:** Universal (transport-agnostic, device-agnostic)  
**Default Topology:** Gateway/Hub orchestrated execution  
**Status:** Definition Freeze for v1.0 baseline

---

## 1. Purpose

Kivai v1.0 defines a stable, universal execution contract that enables AI systems to safely and deterministically control physical devices through structured intents, authorization rules, and standardized device responses.

Kivai v1.0 assumes a **Gateway/Hub** (phone, home hub, router, edge device) as the default orchestrator.

---

## 2. Core Principles

- **Transport-agnostic:** Kivai works over Wi-Fi, BLE, Zigbee/Thread, MQTT, etc.
- **Device-agnostic:** Any device may implement Kivai if it can receive intents and execute actions.
- **Deterministic execution:** Intents must validate, authorize, execute, and return standardized status.
- **Security-first:** Sensitive actions require authorization and proof.
- **Auditability:** Every intent can be tracked via intent_id and status responses.

---

## 3. In-Scope for v1.0 (Must Ship)

### 3.1 Intent Contract
- Stable intent payload format (schema v1.0)
- Targeting model:
  - device_id targeting (primary)
  - zone/location + capability targeting (secondary)
- Validation rules and error responses

### 3.2 Execution API (Device-facing)
- Standard request/response patterns
- Standardized status lifecycle:
  - acknowledged
  - success
  - failed (with reason codes)
  - (Internal implementations may track intermediate states like "executing," but these are not part of the public v1.0 status contract.)

### 3.3 Gateway/Hub Orchestration Model (Default)
- Gateway receives user request (voice/text)
- Gateway generates structured Kivai intent
- Gateway routes to device (direct network delivery)
- Gateway handles retries/timeouts and user-facing feedback

### 3.4 Security Baseline
- Role/permission model for sensitive intents (locks, doors, alarms, payments)
- Token-based authorization proof in intent payloads
- Reject-by-default for sensitive actions if auth is missing/invalid

### 3.5 Minimal Reference Tooling
- Schema validator
- Test harness
- Mock device demo path

---

## 4. Optional for v1.x (Not Required to Ship v1.0)

- Mesh routing / multi-device handoff (device-to-device forwarding)
- Voiceprint biometrics
- Cloud orchestration layer
- Manufacturer certification program
- Marketplace / app ecosystem

---

## 5. Out of Scope (Explicit Non-Goals)

Kivai is NOT:
- An AI assistant
- An NLP or speech-to-text model
- A proprietary device ecosystem
- A replacement for existing assistants

AI interprets human language.  
Kivai standardizes machine execution.

---

## 6. Practical Example (v1.0)

User says: “Kivai, close the patio door.”

Gateway produces:

- intent: close
- target: patio door lock actuator
- auth proof required (owner role)

Device returns:
- acknowledged → success/failed

---

## 7. v1.0 Success Criteria

Kivai v1.0 is considered complete when it provides:

1. Stable schema v1.0 for intents
2. Stable device execution API spec
3. Standard status lifecycle with reason codes
4. Baseline security model for sensitive actions
5. Working reference demo (gateway → mock device → status return)
6. Validation + tests that enforce the above

---

**End of Scope Document**
