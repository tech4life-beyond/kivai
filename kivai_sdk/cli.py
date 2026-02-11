
import argparse
import json
import sys
from pathlib import Path

from kivai_sdk.validator import validate_command
from kivai_sdk.runtime import execute_intent, pretty_json



def _cmd_validate(args: argparse.Namespace) -> int:
    payload_path = Path(args.payload)
    if not payload_path.exists():
        print(f"❌ File not found: {payload_path}", file=sys.stderr)
        return 2

    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to read JSON: {e}", file=sys.stderr)
        return 2

    ok, message = validate_command(payload)
    print(message)
    return 0 if ok else 1


def _cmd_run_echo(args: argparse.Namespace) -> int:
    # v0.1: build a minimal intent payload and execute through runtime pipeline
    payload = {
        "intent": "echo",
        "message": args.message,
        # future: device_id, routing, context, etc.
        "auth": {"required": False},
        "confidence": 1.0,
    }
    ack = execute_intent(payload)
    print(pretty_json(ack))
    return 0 if ack.get("status") == "ok" else 1



def _cmd_serve(args: argparse.Namespace) -> int:
    # Gateway HTTP (FastAPI). Import inside command to avoid import cost when not used.
    try:
        import uvicorn  # type: ignore
    except Exception:
        print("❌ Missing dependency: uvicorn. Install dependencies and try again.", file=sys.stderr)
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
        description="KIVAI v0.1 — Intent standard & gateway reference (Tech4Life & Beyond)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a JSON payload against the canonical Kivai schema")
    p_validate.add_argument("payload", help="Path to JSON file")
    p_validate.set_defaults(func=_cmd_validate)

    p_run = sub.add_parser("run", help="Run a local protocol demo")
    run_sub = p_run.add_subparsers(dest="protocol", required=True)

    p_echo = run_sub.add_parser("echo", help="Echo protocol demo")
    p_echo.add_argument("--message", required=True, help="Message to echo")
    p_echo.set_defaults(func=_cmd_run_echo)

    p_serve = sub.add_parser("serve", help="Run the local Kivai gateway (HTTP)")
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    p_serve.add_argument("--port", type=int, default=8080, help="Bind port (default: 8080)")
    p_serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
