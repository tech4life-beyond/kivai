# Kivai

## K.I.V.A.I.
**Knowledge Interface Voice for Artificial Intelligence**

Kivai is an open interoperability platform that enables any AI assistant to control any device through a standardized intent contract and device API.

Developed and maintained by **Tech4Life & Beyond LLC**, Kivai provides a deterministic, secure, and vendor-neutral execution layer between AI systems and intelligent devices.

---

# Why Kivai Exists

Artificial Intelligence can understand natural language.

However, devices and ecosystems still require a reliable, structured, and interoperable execution contract to:

- Validate intents safely and deterministically  
- Route commands across different devices and brands  
- Share context between multiple devices  
- Enforce authentication and trust layers  
- Avoid ecosystem lock-in  

AI interprets language.  
Kivai standardizes execution.

---

# Platform Architecture (v1.0)

Kivai v1.0 assumes a **Gateway-Orchestrated Model** by default.

## Execution Flow

1. User speaks to an AI assistant.
2. AI generates a structured Kivai intent.
3. A trusted Gateway/Hub validates, authenticates, and routes the intent.
4. Target device (or adapter) executes the command.
5. Device responds with lifecycle status (`acknowledged` / `success` / `failed`).

Mesh networking between devices is optional and not required in v1.0.

---

# Canonical Intent Schema (v1.0)

The official schema is located at:

```
schema/kivai-intent-v1.schema.json
```

This schema defines the universal Kivai intent contract.

## Canonical Example (v1.0)

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

Kivai supports two routing strategies:

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

Devices MUST reject sensitive intents if:

- `auth` is missing  
- Token is invalid or expired  
- Role is insufficient  

---

# Response Lifecycle

Devices MUST respond with:

- `intent_id`
- `status` (`acknowledged` | `success` | `failed`)
- `device_id`
- `timestamp`

On failure:

```json
{
  "intent_id": "c9c4c8d1-2d6f-4d6c-9a2f-1f2c3a4b5c6d",
  "status": "failed",
  "device_id": "door-patio-01",
  "timestamp": "2026-02-06T21:10:01Z",
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Owner authentication required"
  }
}
```

---

# Repository Structure

- `schema/` — canonical intent schema (v1.0)
- `schema/legacy/` — archived pre-v1 drafts (historical reference only)
- `docs/` — protocol documentation and architectural notes
- `kivai_sdk/` — reference SDK utilities
- `mock-devices/` — local mock device servers for testing
- `tests/` — automated test suite
- `transcription/` — experimental transcription utilities

---

# Development Status

## Current Phase

- v1.0 Intent Specification Formalized
- Canonical JSON Schema Defined
- Reference SDK under migration
- Gateway-Orchestrated Model defined
- Security baseline established

## Next Phase

- SDK alignment to v1.0 schema
- Device adapter reference implementation
- Auth validation layer prototype
- Gateway reference design

---

## v0.2 Adapter Interface (How to extend execution)

Kivai executes intents through adapters.

- Adapter contract: `kivai_sdk/adapters/base.py`
- Registry: `kivai_sdk/adapters/registry.py`

To add a new intent:
1) Implement an adapter with `intent = "<intent_name>"` and `execute(payload, ctx)`.
2) Register it in `default_registry()`.

The runtime returns a stable ACK envelope and places adapter output under `result`.

---

# Licensing

This project is licensed under the **Tech4Life Open Impact License (TOIL) v1.0**.

Commercial manufacturing, distribution, or commercial exploitation requires a signed **TOIL Royalty Agreement** with **Tech4Life & Beyond LLC**.

See the official TOIL repository within this organization for full license terms.

Unauthorized commercial use is prohibited.

---

# Organization

Maintained by:

**Tech4Life & Beyond LLC**  
Florida, United States  

Part of the Tech4Life Operating System ecosystem.

---

# Official TOIL Product Pack

The canonical TOIL Product Pack for the Kivai Platform  
(registration, ethics framework, and licensing readiness)  
is maintained in the Tech4Life products repository:

https://github.com/tech4life-beyond/products/tree/main/kivai

Product ID: T4L-TOIL-002-KIVAI

This repository contains the technical implementation layer of the Kivai Platform.
