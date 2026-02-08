# Kivai Intent API

The Intent API defines how devices and services should handle structured Kivai intents on the Kivai Platform.

It acts as the bridge between natural language and real-world action.

---

## 🔁 Request Format

The device or service receives a v1.0 intent payload like:

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

## 📥 Handling the Request

When a device receives a request, it should:

1. **Parse** the payload  
2. **Validate + authorize** per device capability and security rules  
3. **Execute** the requested intent  
4. **Respond** with a status update  

---

## 🔁 Response Format

Devices that receive a Kivai intent should respond using a standard format like this:

```json
{
  "intent_id": "c9c4c8d1-2d6f-4d6c-9a2f-1f2c3a4b5c6d",
  "status": "success",
  "device_id": "kitchen-light-01",
  "timestamp": "2026-02-06T21:10:01Z"
}
```

### ✅ Required fields:

- **intent_id**: ID of the intent being acknowledged or completed  
- **status**: `acknowledged` | `success` | `failed`  
- **device_id**: Unique device identifier  
- **timestamp**: When the response was generated (ISO 8601 format)  

On failure, include an `error` object with a code and message.

This format ensures consistency across devices and services, and makes debugging easier.

---

## Compatibility / Legacy Notes

Pre-v1.0 drafts used `command`, `object`, and `location` fields for requests. The v1.0 Intent API standardizes on `intent`, `target`, and `meta`.
