"""Offline checks: python -m unittest discover -s tests -p 'test_voice_support.py'."""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "tools"))

import voice_support  # noqa: E402


class KnowledgeBaseTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_delegates_to_support_namespace_and_preserves_results(self):
        response = {
            "results": [{
                "entry_id": "customer-document",
                "content": "A passage from the connected customer documentation.",
                "namespace": "support.accounts",
                "score": 0.91,
                "metadata": {"source": "customer-help-center"},
            }],
        }
        query = "Wie kann ich mein Passwort zurücksetzen?"
        with patch.object(voice_support, "retrieval_query", new_callable=AsyncMock, return_value=response) as retrieval:
            result = await voice_support.search_knowledge_base(query)
        retrieval.assert_awaited_once_with(query, namespace="support", max_results=3)
        self.assertIs(result, response)

    async def test_search_preserves_empty_results_and_returned_errors(self):
        for response in ({"results": []}, {"results": [], "error": "Retrieval timed out"}):
            with self.subTest(response=response):
                with patch.object(voice_support, "retrieval_query", new_callable=AsyncMock, return_value=response):
                    result = await voice_support.search_knowledge_base("Customer question")
                self.assertIs(result, response)

    async def test_lookup_exception_is_not_disguised_as_missing_knowledge(self):
        with patch.object(voice_support, "retrieval_query", new_callable=AsyncMock, side_effect=RuntimeError("Lookup unavailable")):
            with self.assertRaisesRegex(RuntimeError, "Lookup unavailable"):
                await voice_support.search_knowledge_base("Customer question")


class MockTicketTests(unittest.TestCase):
    def setUp(self):
        self.request = {
            "summary": "Password reset still fails",
            "description": "Requested a new link and checked spam; no email arrived.",
            "customer_email": "Alex@example.com",
            "confirmed": True,
            "context": {"run_id": "demo-run-1"},
        }

    def test_requires_explicit_confirmation(self):
        for confirmed in (False, None, "true", 1):
            with self.subTest(confirmed=confirmed):
                result = voice_support.create_mock_ticket(**{**self.request, "confirmed": confirmed})
                self.assertEqual(result["error"], "caller_confirmation_required")
                self.assertNotIn("ticket_id", result)
        request = {key: value for key, value in self.request.items() if key != "confirmed"}
        self.assertEqual(voice_support.create_mock_ticket(**request)["error"], "caller_confirmation_required")

    def test_returns_explicit_mock_receipt_without_network_or_storage(self):
        with patch("socket.socket", side_effect=AssertionError("Network access is not allowed")), patch(
            "builtins.open", side_effect=AssertionError("Ticket storage is not allowed")
        ):
            result = voice_support.create_mock_ticket(**self.request)
        self.assertEqual(result["status"], "mock_created")
        self.assertTrue(result["mock"])
        self.assertFalse(result["persisted"])
        self.assertFalse(result["dispatched"])
        self.assertRegex(result["ticket_id"], r"^DEMO-[A-F0-9]{8}$")
        self.assertEqual(result["customer_email"], "alex@example.com")
        self.assertEqual(result["run_id"], "demo-run-1")

    def test_repeated_request_has_stable_demo_reference(self):
        first = voice_support.create_mock_ticket(**self.request)
        self.assertEqual(first, voice_support.create_mock_ticket(**self.request))
        changed = voice_support.create_mock_ticket(**{**self.request, "summary": "A separate issue"})
        self.assertNotEqual(first["ticket_id"], changed["ticket_id"])

    def test_rejects_incomplete_or_invalid_details(self):
        cases = [
            ({"summary": " "}, "summary_and_description_required"),
            ({"description": ""}, "summary_and_description_required"),
            ({"customer_email": "alex at example.com"}, "valid_contact_email_required"),
            ({"priority": "urgent"}, "invalid_priority"),
        ]
        for overrides, expected in cases:
            with self.subTest(overrides=overrides):
                result = voice_support.create_mock_ticket(**{**self.request, **overrides})
                self.assertEqual(result["error"], expected)
                self.assertNotIn("ticket_id", result)


if __name__ == "__main__":
    unittest.main()
