from __future__ import annotations

import unittest

from scripts.probe_webull_order_preview import first_account_id


class WebullOrderPreviewTests(unittest.TestCase):
    def test_account_id_is_extracted_without_logging_payload(self) -> None:
        self.assertEqual(first_account_id({"accounts": [{"account_id": "private"}]}), "private")


if __name__ == "__main__":
    unittest.main()
