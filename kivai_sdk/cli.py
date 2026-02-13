import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from kivai_sdk.runtime import execute_intent, pretty_json
from kivai_sdk.validator import validate_command


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_canonical_payload(
    *,
    intent: str,
    target: dict,
    params: dict | None = None,
    auth: dict | None = None,
    language: str = "en",
    confidence: float = 1.0,
    source: str = "cli",
) -> dict:
    payload = {
        "intent_id": str(uuid.uuid4()),
        "intent": intent,
        "target": target,
        "params": params or {},
        "meta": {
            "timestamp": _utc_now_iso(),
            "language": language,
            "confidence": float(confidence),
            "source": source,
        },
    }
    if auth is not None:
        payload["auth"] = auth
    return payload


def _read_json_file(path: str) -> dict:
    payload_path = Path(path)
    if not payload_path.exists():
        raise FileNotFoundError(f"File not found: {payload_path}")

    data = json.loads(payload_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Payload JSON must be an object")
    return data


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        payload = _read_json_file(args.payload)
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    ok, message = validate_command(payload)
    print(message)
    return 0 if ok else 1


def _cmd_execute(args: argparse.Namespace) -> int:
    """
    Execute a payload from file and print the ACK.
    Note: runtime may allow non-schema demo intents (e.g., echo).
    """
    try:
        payload = _read_json_file(args.payload)
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2

    ack = execute_intent(payload)
    print(pretty_json(ack))
    return 0 if ack.get("status") == "ok" else 1


def _cmd_run_echo(args: argparse.Namespace) -> int:
    payload = _make_canonical_payload(
        intent="echo",
        target={"capability": "speaker", "zone": "living_room"},
        params={"message": args.message},
        auth=None,
        language="en",
        confidence=1.0,
    )
    ack = execute_intent(payload)
    print(pretty_json(ack))
    return 0 if ack.get("status") == "ok" else 1


def _cmd_list_adapters(args: argparse.Namespace) -> int:
    # Introspection is intentional for CLI output in v0.10
    from kivai_sdk.adapters import default_registry

    reg = default_registry()

    items: list[dict] = []
    by_intent = getattr(reg, "_by_intent", {})
    if isinstance(by_intent, dict):
        for intent, adapter in sorted(by_intent.items()):
            cap_obj = None
            try:
                cap_obj = getattr(adapter, "capabilities", None)
            except Exception:
                cap_obj = None

            required_caps = []
            requires_auth = False
            required_role = None

            if cap_obj is not None:
                try:
                    # property -> object, callable -> call
                    c = cap_obj() if callable(cap_obj) else cap_obj
                    requires_auth = bool(getattr(c, "requires_auth", False))
                    required_role = getattr(c, "required_role", None)
                    req = getattr(c, "required_capabilities", frozenset())
                    if isinstance(req, (set, frozenset, list, tuple)):
                        required_caps = sorted([x for x in req if isinstance(x, str)])
                except Exception:
                    pass

            items.append(
                {
                    "intent": intent,
                    "adapter": adapter.__class__.__name__,
                    "requires_auth": requires_auth,
                    "required_role": required_role,
                    "required_capabilities": required_caps,
                }
            )

    print(
        json.dumps({"adapters": items}, indent=2, ensure_ascii=False, sort_keys=False)
    )
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    # Gateway HTTP (FastAPI). Import inside command to avoid dependency when not used.
    try:
        import uvicorn  # type: ignore
    except Exception:
        print(
            "❌ Missing dependency: uvicorn. Install dependencies and try again.",
            file=sys.stderr,
        )
        return 2

    try:
        from kivai_sdk.gateway import app
    except Exception as e:
        print(f"❌ Failed to import gateway: {e}", file=sys.stderr)
        return 2

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kivai",
        description="KIVAI — Intent standard & gateway reference (Tech4Life & Beyond)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser(
        "validate", help="Validate a JSON payload against the canonical Kivai schema"
    )
    p_validate.add_argument("payload", help="Path to JSON file")
    p_validate.set_defaults(func=_cmd_validate)

    p_execute = sub.add_parser(
        "execute", help="Execute a JSON payload and print ACK (local runtime)"
    )
    p_execute.add_argument("payload", help="Path to JSON file")
    p_execute.set_defaults(func=_cmd_execute)

    p_list = sub.add_parser("list", help="List local registry items")
    list_sub = p_list.add_subparsers(dest="list_what", required=True)

    p_list_adapters = list_sub.add_parser("adapters", help="List available adapters")
    p_list_adapters.set_defaults(func=_cmd_list_adapters)

    p_run = sub.add_parser("run", help="Run a local protocol demo")
    run_sub = p_run.add_subparsers(dest="protocol", required=True)

    p_echo = run_sub.add_parser("echo", help="Echo protocol demo")
    p_echo.add_argument("--message", required=True, help="Message to echo")
    p_echo.set_defaults(func=_cmd_run_echo)

    p_serve = sub.add_parser("serve", help="Run the local Kivai gateway (HTTP)")
    p_serve.add_argument(
        "--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)"
    )
    p_serve.add_argument(
        "--port", type=int, default=8080, help="Bind port (default: 8080)"
    )
    p_serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
