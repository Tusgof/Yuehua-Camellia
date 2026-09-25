"""Bounded, read-only Webull Thailand capability check.

Prints only endpoint status and public instrument metadata. Never prints account
payloads, identifiers, credentials, or tokens.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


AUTH_PATHS = {
    "/openapi/auth/token/create",
    "/openapi/auth/token/check",
    "/openapi/auth/token/refresh",
}
READ_PATHS = {
    "/openapi/account/list",
    "/openapi/assets/balance",
    "/openapi/assets/positions",
    "/openapi/instrument/stock/list",
}
SYMBOLS = ("VTI", "EWJ", "VWO", "GLD", "XLE", "SHY", "DBC", "IPAC")


def guard_requests(client: Any) -> list[str]:
    paths: list[str] = []
    original = client.get_response

    def guarded(request: Any) -> Any:
        path = str(request.get_action_name())
        if path not in AUTH_PATHS | READ_PATHS:
            raise RuntimeError("endpoint_not_allowed")
        if path in READ_PATHS and sum(p in READ_PATHS for p in paths) >= 4:
            raise RuntimeError("read_request_limit")
        paths.append(path)
        return original(request)

    client.get_response = guarded
    return paths


def first_account_id(value: Any) -> str:
    if isinstance(value, dict):
        if value.get("account_id"):
            return str(value["account_id"])
        for child in value.values():
            found = first_account_id(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = first_account_id(child)
            if found:
                return found
    return ""


def instrument_rows(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if value.get("symbol") in SYMBOLS:
            rows.append({
                "symbol": value["symbol"],
                "status": value.get("status"),
                "fractionable": value.get("fractionable"),
            })
        for child in value.values():
            rows.extend(instrument_rows(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(instrument_rows(child))
    return rows


def checked_json(response: Any) -> Any:
    if response.status_code != 200:
        raise RuntimeError(f"http_{response.status_code}")
    return response.json()


def worker() -> dict[str, Any]:
    key = os.environ.get("WEBULL_APP_KEY") or os.environ.get("CAMELLIA_WEBULL_APP_KEY")
    secret = os.environ.get("WEBULL_APP_SECRET") or os.environ.get("CAMELLIA_WEBULL_APP_SECRET")
    if not key or not secret:
        raise RuntimeError("credentials_missing")
    appdata = os.environ.get("LOCALAPPDATA")
    if not appdata:
        raise RuntimeError("localappdata_missing")

    import webull
    from webull.core.client import ApiClient
    from webull.core.http.initializer.token.token_manager import TokenManager
    from webull.core.request import ApiRequest
    from webull.trade.trade.v2.account_info_v2 import AccountV2

    if sys.version_info[:2] != (3, 11) or webull.__version__ != "2.0.13":
        raise RuntimeError("runtime_or_sdk_version_mismatch")
    logging.disable(logging.CRITICAL)
    client = ApiClient(
        key, secret, "th", connect_timeout=8, timeout=8,
        auto_retry=False, token_check_duration_seconds=12,
        token_check_interval_seconds=3,
    )
    client.add_endpoint("th", "api.webull.co.th")
    client._file_logger_set = True
    client._stream_logger_set = True
    paths = guard_requests(client)
    token_dir = Path(appdata) / "Yuehua-Camellia" / "webull-token"
    TokenManager(str(token_dir)).init_token(client)

    account_api = AccountV2(client)
    accounts = checked_json(account_api.get_account_list())
    account_id = first_account_id(accounts)
    if not account_id:
        raise RuntimeError("account_id_missing")
    checked_json(account_api.get_account_balance(account_id))
    checked_json(account_api.get_account_position(account_id))
    request = ApiRequest(
        "/openapi/instrument/stock/list", version="v2", method="GET",
        query_params={"symbols": ",".join(SYMBOLS), "category": "US_STOCK", "page_size": 100},
    )
    instruments = instrument_rows(checked_json(client.get_response(request)))
    unique = {row["symbol"]: row for row in instruments}
    if len(unique) != len(SYMBOLS):
        raise RuntimeError("instrument_metadata_incomplete")
    return {
        "status": "pass",
        "region": "th",
        "host": "api.webull.co.th",
        "python": ".".join(map(str, sys.version_info[:3])),
        "sdk": webull.__version__,
        "account_list": "ok",
        "balance": "ok",
        "positions": "ok",
        "instruments": [unique[symbol] for symbol in SYMBOLS],
        "read_paths": [path for path in paths if path in READ_PATHS],
        "order_calls": 0,
    }


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--worker":
        try:
            print(json.dumps(worker(), sort_keys=True))
            return 0
        except Exception as exc:
            if isinstance(exc, RuntimeError):
                reason = str(exc)
            elif callable(getattr(exc, "get_error_code", None)):
                code = exc.get_error_code()
                reason = "token_pending_2fa" if code == "ERROR_INIT_TOKEN" else f"sdk_{code}"
            else:
                reason = exc.__class__.__name__
            print(json.dumps({"status": "blocked", "reason": reason}, sort_keys=True))
            return 1
    try:
        result = subprocess.run(
            [sys.executable, __file__, "--worker"],
            capture_output=True, text=True, timeout=40, check=False,
        )
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "blocked", "reason": "read_only_probe_timeout_40s"}))
        return 1
    try:
        payload = json.loads(result.stdout)
    except (ValueError, TypeError):
        payload = {"status": "blocked", "reason": "probe_failed_without_safe_result"}
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
