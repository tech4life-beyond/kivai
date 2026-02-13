# KIVAI v1.0 — Device Adapter Interface (Canonical)

This document defines the **canonical interface** between a KIVAI runtime (gateway/hub) and any physical or digital device.

KIVAI is deterministic, auditable, and production-oriented.
KIVAI is not a chatbot.
KIVAI is infrastructure.

---

# 1. Deployment Model (v1.0 Baseline)

KIVAI v1.0 assumes a **Gateway-Orchestrated Runtime** by default.

The runtime lives on:

- Laptop / Desktop (development)
- Raspberry Pi / Home Hub
- Edge server / Appliance
- Industrial controller

Devices do NOT need to embed KIVAI.
They only need an adapter or bridge.

---

# 2. Canonical Intent Contract (Input)

The official schema is located at:

```
schema/kivai-intent-v1.schema.json
```

Minimum required structure:

- intent_id (string)
- intent (string)
- target (device_id OR capability + zone)
- params (object)
- meta (timestamp, language, confidence, source)
- optional auth (required_role + token)

Example:

```json
{
  "intent_id": "abc-123",
  "intent": "set_temperature",
  "target": {
    "capability": "thermostat",
    "zone": "living_room"
  },
  "params": {
    "value": 21,
    "unit": "C"
  },
  "meta": {
    "timestamp": "2026-02-13T20:00:00Z",
    "language": "en",
    "confidence": 1.0,
    "source": "gateway"
  }
}
```

Adapters MUST NOT accept free-form text.
Only schema-valid structured payloads.

---

# 3. ACK Envelope (Output)

Runtime MUST return a deterministic ACK envelope.

Required fields:

- execution_id
- intent_id
- timestamp
- status ("ok" | "failed")
- intent

Optional fields:

- device_id
- route
- result
- error

Example success:

```json
{
  "execution_id": "exec-001",
  "intent_id": "abc-123",
  "timestamp": "2026-02-13T20:00:01Z",
  "status": "ok",
  "intent": "set_temperature",
  "device_id": "thermostat-living-01",
  "result": {
    "action": "set_temperature",
    "value": 21.0,
    "unit": "C"
  }
}
```

Example failure:

```json
{
  "execution_id": "exec-002",
  "intent_id": "abc-123",
  "timestamp": "2026-02-13T20:00:01Z",
  "status": "failed",
  "intent": "unlock_door",
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authorization failed"
  }
}
```

Error codes are machine-readable and deterministic.

---

# 4. Adapter Responsibilities

An adapter is a deterministic execution unit bound to a single intent.

It MUST:

- Declare `intent`
- Implement `execute(payload, ctx)`
- Return normalized adapter output
- Declare AdapterCapabilities (strict mode)

It MUST NOT:

- Perform authorization decisions
- Accept natural language
- Mutate global runtime state

---

# 5. Adapter Execution Contract

Adapters return raw output that is normalized by runtime.

Canonical normalized structure:

Success:

```json
{
  "ok": true,
  "data": { ... }
}
```

Failure:

```json
{
  "ok": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid parameter"
  }
}
```

Runtime converts this into the ACK envelope.

---

# 6. Routing Model

Routing is resolved by runtime using:

- target.device_id
- OR target.capability + target.zone

In strict mode, runtime verifies:

- Adapter required_capabilities
- Device capabilities match

If incompatible:

ADAPTER_CAPABILITY_MISMATCH is returned.

---

# 7. Authorization Model

Authorization is evaluated by runtime policy.

Adapters declare baseline requirements.

Sensitive intents (example: unlock_door) require auth proof.

If proof is missing or invalid:

AUTH_REQUIRED is returned deterministically.

---

# 8. Physical Integration Example (TV Remote)

Scenario: Add KIVAI control to a TV remote.

Hardware:

- ESP32 module
- BLE or WiFi connectivity
- IR emitter (optional)

Flow:

1. Button press → module sends event to gateway.
2. Gateway builds canonical KIVAI intent.
3. Runtime validates + authorizes + routes.
4. TV adapter executes via IR or LAN API.
5. ACK is returned.

KIVAI lives in the gateway runtime.
The remote only emits structured events.

---

# 9. What “Universal” Means

Universal does NOT mean:

- Every device behavior is built-in.

Universal DOES mean:

- All devices share the same intent contract.
- Routing, authorization, and auditing are standardized.
- Device-specific logic lives only in adapters.

The contract remains stable.
Adapters evolve independently.

---

End of Canonical Device Adapter Interface (v1.0)
