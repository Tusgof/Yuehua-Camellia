"""Bounded production preview probe; never places, replaces, or cancels orders."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ALLOWED = {
    "/openapi/auth/token/create",
    "/openapi/auth/token/check",
    "/openapi/auth/token/refresh",
    "/openapi/account/list",
    "/openapi/config",
    "/openapi/trade/order/preview",
}


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


def run_worker() -> dict[str, Any]:
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
    from webull.trade.trade.v2.account_info_v2 import AccountV2
    from webull.trade.trade_client import TradeClient

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
    paths: list[str] = []
    original = client.get_response

    def guarded(request: Any) -> Any:
        path = str(request.get_action_name())
        if path not in ALLOWED:
            raise RuntimeError(f"endpoint_not_allowed:{path}")
        if path == "/openapi/trade/order/preview" and paths.count(path) >= 2:
            raise RuntimeError("preview_request_limit")
        paths.append(path)
        return original(request)

    client.get_response = guarded
    token_dir = Path(appdata) / "Yuehua-Camellia" / "webull-token"
    token_manager = TokenManager(str(token_dir))
    local_token = token_manager.load_token_from_local()
    if not local_token or local_token.status != "NORMAL" or not local_token.token:
        raise RuntimeError("local_token_not_normal")
    client.set_token(local_token.token)
    account_payload = AccountV2(client).get_account_list().json()
    account_id = first_account_id(account_payload)
    if not account_id:
        raise RuntimeError("account_id_missing")

    order = {
        "combo_type": "NORMAL",
        "client_order_id": "CAMELLIA_PREVIEW_01",
        "symbol": "VTI",
        "instrument_type": "EQUITY",
        "market": "US",
        "order_type": "MARKET",
        "quantity": "0.01",
        "side": "BUY",
        "time_in_force": "DAY",
        "entrust_type": "QTY",
        "support_trading_session": "CORE",
    }
    order_operation = TradeClient.__init__.__globals__["OrderOperationV3"](client)
    results = []
    for order_type in ("MARKET", "MOO"):
        candidate = dict(order)
        candidate["order_type"] = order_type
        try:
            response = order_operation.preview_order(account_id, [candidate])
            status_code = getattr(response, "status_code", None)
            payload = response.json()
            row: dict[str, Any] = {
                "status": "accepted" if status_code == 200 else "rejected",
                "http_status": status_code,
                "preview_only": True,
                "orders_sent": 0,
                "symbol": "VTI",
                "quantity": "0.01",
                "order_type": order_type,
                "time_in_force": "DAY",
                "support_trading_session": "CORE",
            }
            if status_code == 200:
                row["estimated_cost_present"] = isinstance(payload, dict) and "estimated_cost" in payload
                row["estimated_fee_present"] = isinstance(payload, dict) and "estimated_transaction_fee" in payload
            else:
                row["error_code"] = payload.get("error_code") if isinstance(payload, dict) else None
                row["error_message_present"] = isinstance(payload, dict) and bool(payload.get("message"))
            results.append(row)
        except Exception as exc:
            if callable(getattr(exc, "get_error_code", None)):
                results.append({"status": "rejected", "preview_only": True, "orders_sent": 0, "order_type": order_type, "error_code": exc.get_error_code()})
            else:
                raise
    return {"status": "pass", "preview_only": True, "orders_sent": 0, "results": results, "request_paths": paths}


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--worker":
        try:
            print(json.dumps(run_worker(), sort_keys=True))
            return 0
        except Exception as exc:
            if callable(getattr(exc, "get_error_code", None)):
                reason = f"sdk_{exc.get_error_code()}"
            elif isinstance(exc, RuntimeError):
                reason = str(exc)
            else:
                reason = exc.__class__.__name__
            print(json.dumps({"status": "blocked", "reason": reason}, sort_keys=True))
            return 1
    try:
        proc = subprocess.run([sys.executable, __file__, "--worker"], capture_output=True, text=True, timeout=40, check=False)
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "blocked", "reason": "preview_probe_timeout_40s"}))
        return 1
    print(proc.stdout.strip() or json.dumps({"status": "blocked", "reason": "no_safe_result"}))
    return 0 if '"status": "accepted"' in proc.stdout else 1


if __name__ == "__main__":
    raise SystemExit(main())
