# KIVAI

## K.I.V.A.I.
**Knowledge Interface & Validation Architecture for Interoperability**

KIVAI is an open interoperability platform that standardizes how AI systems interact with physical and digital devices.

It provides a deterministic, auditable, and vendor-neutral execution layer between AI-generated intents and real-world device actions.

Developed and maintained by **Tech4Life & Beyond LLC**, KIVAI is infrastructure — not a chatbot, not an assistant, and not a SaaS product.

AI interprets language.
KIVAI standardizes execution.

---

# Why KIVAI Exists

Artificial Intelligence can understand natural language.

However, devices require a reliable and structured execution contract to:

- Validate intents safely and deterministically  
- Route commands across different devices and brands  
- Enforce authentication and authorization policies  
- Provide auditability and traceability  
- Avoid ecosystem lock-in  

Without a shared contract, AI-to-device interaction becomes fragile, unsafe, and vendor-controlled.

KIVAI defines the contract.

---

# What KIVAI Is

KIVAI is:

- An **Intent Standard (canonical schema)**  
- A **Routing Model (device_id or capability + zone)**  
- A **Security & Authorization baseline**  
- An **Adapter execution layer**  
- An **Audit-capable runtime**  

KIVAI is NOT:

- A conversational AI  
- A device manufacturer  
- A UI layer  
- A cloud-only SaaS  

It is infrastructure designed for long-term interoperability.

---

# Platform Architecture (v1.0)

KIVAI v1.0 assumes a **Gateway-Orchestrated Model** by default.

## Execution Flow

1. A user speaks to an AI assistant.
2. The AI generates a structured KIVAI intent.
3. A trusted Gateway validates, authenticates, and routes the intent.
4. A device adapter executes the action.
5. The runtime returns a deterministic ACK envelope.

Mesh networking between devices is optional and not required in v1.0.

---

# Canonical Intent Schema (v1.0)

The official schema is located at:

```
schema/kivai-intent-v1.schema.json
```

This schema defines the universal KIVAI intent contract.

## Canonical Example

```json
{
  "intent_id": "c9c4c8d1-2d6f-4d6c-9a2f-1f2c3a4b5c6d",
  "intent": "turn_on",
  "target": {
    "capability": "light_control",
    "zone": "kitchen"
  },
  "params": {
    "level": 100
  },
  "meta": {
    "timestamp": "2026-02-06T21:10:00Z",
    "language": "en",
    "confidence": 0.97,
    "source": "gateway",
    "trigger": "Kivai"
  }
}
```

---

# Targeting Model

KIVAI supports two routing strategies:

## 1. Direct Device Targeting (Preferred)

```json
"target": {
  "device_id": "door-patio-01"
}
```

## 2. Capability + Zone Targeting (Fallback)

```json
"target": {
  "capability": "lock_control",
  "zone": "patio"
}
```

At least one of the following MUST be present:

- `device_id`
- OR (`capability` + `zone`)

---

# Security Baseline

Sensitive intents (locks, payments, alarms, surveillance, safety actuators) require an `auth` object.

```json
"auth": {
  "required_role": "owner",
  "token": "signed-session-token"
}
```

The runtime MUST:

- Reject missing authorization for protected intents  
- Return deterministic error codes  
- Never mask authorization failures as schema errors  

---

# ACK / Execution Envelope

Every execution returns a stable response envelope containing:

- `execution_id` (trace ID)
- `intent_id`
- `timestamp`
- `status` (`ok` | `failed`)
- `intent`
- optional `device_id`
- optional `route`
- `result` (on success)
- `error` (on failure)

Example failure:

```json
{
  "execution_id": "e5d4...",
  "intent_id": "c9c4...",
  "timestamp": "2026-02-06T21:10:01Z",
  "status": "failed",
  "intent": "unlock_door",
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Owner authentication required"
  }
}
```

---

# Repository Structure

- `schema/` — Canonical intent schema (v1.0)
- `docs/` — Architecture and deployment documentation
- `kivai_sdk/` — Reference runtime & SDK implementation
- `tests/` — Automated validation suite
- `mock-devices/` — Local mock devices for integration testing

---

# Current Implementation Status

KIVAI currently includes:

- Canonical JSON Schema v1.0
- Strict-mode runtime
- Policy-driven authorization
- Adapter capability contracts
- Execution ID + audit event emission
- Gateway reference implementation (FastAPI)
- CLI tooling
- Deterministic ACK envelope

The project operates under structured CI, semantic versioning discipline, and strict schema alignment.

---

# Extending KIVAI (Adapters)

KIVAI executes intents through adapters.

To add a new device capability:

1. Implement an adapter with:
   - `intent = "<intent_name>"`
   - `execute(payload, ctx)`
2. Declare adapter capability requirements.
3. Register it in the adapter registry.

Adapters must be deterministic and must not implement authorization logic (handled by runtime policy).

See:

```
docs/device-adapter-interface.md
```

---

# Deployment Model

v1.0 assumes a Gateway-Orchestrated Model.

KIVAI can run on:

- Laptop / Desktop (development)
- Raspberry Pi / Home Hub (pilot)
- Edge server / appliance (production)

Future deployment models (embedded runtime and portable module) are documented in `docs/`.

---

# Licensing

Licensed under the **Tech4Life Open Impact License (TOIL) v1.0**.

Commercial manufacturing, distribution, or commercial exploitation requires a signed TOIL Royalty Agreement with **Tech4Life & Beyond LLC**.

Unauthorized commercial use is prohibited.

---

# Organization

Maintained by:

**Tech4Life & Beyond LLC**  
Florida, United States

Part of the Tech4Life Operating System ecosystem.

---

# Official TOIL Product Pack

The canonical TOIL Product Pack for the KIVAI Platform is maintained in the Tech4Life products repository:

https://github.com/tech4life-beyond/products/tree/main/kivai

Product ID: T4L-TOIL-002-KIVAI

This repository contains the technical implementation layer of the KIVAI Platform.
