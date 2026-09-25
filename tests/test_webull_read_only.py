from __future__ import annotations

import unittest

from scripts.check_webull_read_only import first_account_id, guard_requests, instrument_rows


class FakeRequest:
    def __init__(self, path: str) -> None:
        self.path = path

    def get_action_name(self) -> str:
        return self.path


class FakeClient:
    def get_response(self, request: FakeRequest) -> str:
        return request.path


class WebullReadOnlyTests(unittest.TestCase):
    def test_guard_allows_reads_and_rejects_orders(self) -> None:
        client = FakeClient()
        paths = guard_requests(client)
        self.assertEqual(client.get_response(FakeRequest("/openapi/account/list")), "/openapi/account/list")
        with self.assertRaisesRegex(RuntimeError, "endpoint_not_allowed"):
            client.get_response(FakeRequest("/openapi/trade/order/place"))
        self.assertEqual(paths, ["/openapi/account/list"])

    def test_private_account_id_is_found_without_serializing_payload(self) -> None:
        self.assertEqual(first_account_id({"data": [{"account_id": "private"}]}), "private")

    def test_instrument_summary_excludes_private_fields(self) -> None:
        rows = instrument_rows({"data": [{"symbol": "VTI", "status": "OC", "fractionable": True, "account_id": "private"}]})
        self.assertEqual(rows, [{"symbol": "VTI", "status": "OC", "fractionable": True}])


if __name__ == "__main__":
    unittest.main()
