import copy
import io
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from unittest.mock import patch

import app

NOTES = "Build a home page and a contact page. No online payments. We might need a newsletter later."
SCOPE = {"deliverables": [{"task": "Home and contact pages", "source": "Build a home page and a contact page."}],
         "exclusions": [{"task": "Online payments", "source": "No online payments."}],
         "questions": ["Should the newsletter be part of this version?"]}


def quote_data():
    return {"project": "Fictional website", "notes": NOTES, "scope": copy.deepcopy(SCOPE),
            "rate": "100.05", "currency": "INR", "hours": ["1.5"], "reviewed": True}


class ScopeTests(unittest.TestCase):
    def test_source_quote_must_be_in_notes(self):
        scope = copy.deepcopy(SCOPE)
        scope["deliverables"][0]["source"] = "The client requested an analytics dashboard."
        with self.assertRaisesRegex(ValueError, "not found"):
            app.validate_scope(scope, NOTES)

    def test_exclusions_need_evidence_too(self):
        scope = copy.deepcopy(SCOPE)
        scope["exclusions"][0]["source"] = "No mobile support is required."
        with self.assertRaisesRegex(ValueError, "not found"):
            app.validate_scope(scope, NOTES)

    def test_empty_or_invalid_scope_is_rejected(self):
        for scope in (None, {}, {**SCOPE, "deliverables": []}, {**SCOPE, "questions": "maybe"}):
            with self.subTest(scope=scope), self.assertRaises(ValueError):
                app.validate_scope(scope, NOTES)

    def test_decimal_rounding_and_total_ignore_browser_amount(self):
        data = quote_data()
        data["total"] = "1.00"
        data["scope"]["deliverables"][0]["amount"] = "1.00"
        result = app.make_quote(data)
        self.assertEqual(result["total"], "150.08")
        self.assertIn("TOTAL: INR 150.08", result["document"])
        self.assertIn("QUESTIONS TO CONFIRM", result["document"])

    def test_per_line_rounding_is_used_in_sum(self):
        data = quote_data()
        data["scope"]["deliverables"] *= 2
        data["hours"] = ["1.5", "1.5"]
        self.assertEqual(app.make_quote(data)["total"], "300.16")

    def test_unreviewed_scope_cannot_export(self):
        data = quote_data(); data["reviewed"] = False
        with self.assertRaisesRegex(ValueError, "Review"):
            app.make_quote(data)

    def test_invalid_estimates_are_rejected(self):
        for value in ("0", "-1", "NaN", "Infinity", "1.001", "1000001", "oops", 42):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = quote_data(); data["rate"] = value; app.make_quote(data)
        for hours in ([], ["0"], ["NaN"], ["10001"], ["2", "3"]):
            with self.subTest(hours=hours), self.assertRaises(ValueError):
                data = quote_data(); data["hours"] = hours; app.make_quote(data)

    def test_changed_source_cannot_reuse_old_scope(self):
        data = quote_data(); data["notes"] = "Build a completely different project with no website."
        with self.assertRaisesRegex(ValueError, "not found"):
            app.make_quote(data)

    def test_model_truncation_and_invalid_json_fail_closed(self):
        for answer in ({"done_reason": "length"}, {"message": {"content": "not JSON"}}, {}):
            with self.subTest(answer=answer), patch("app.urlopen", return_value=io.BytesIO(json.dumps(answer).encode())):
                with self.assertRaises(ValueError): app.extract_scope(NOTES)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def test_assets_serve_independent_of_working_directory(self):
        for path in ("/", "/app.js", "/style.css"):
            with urlopen(self.url + path) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 100)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url + "/../app.py")
        self.assertEqual(error.exception.code, 404)

    def test_cross_origin_request_is_rejected_before_inference(self):
        req = Request(self.url + "/api/extract", b'{"notes":"private brief"}',
                      {"Content-Type": "application/json", "Origin": "https://unrelated.example"})
        with self.assertRaises(HTTPError) as error: urlopen(req)
        self.assertEqual(error.exception.code, 403)

    def test_bad_request_and_model_outage_are_reported(self):
        for body, expected in ((b'[]', 422), (b'not json', 422), (b'{"notes":"Build a small website please."}', 503)):
            with patch("app.urlopen", side_effect=URLError("offline")):
                req = Request(self.url + "/api/extract", body, {"Content-Type": "application/json"})
                with self.assertRaises(HTTPError) as error: urlopen(req)
                self.assertEqual(error.exception.code, expected)
                self.assertIn("error", json.load(error.exception))


if __name__ == "__main__":
    unittest.main()
