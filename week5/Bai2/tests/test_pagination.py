import unittest
from urllib.parse import quote

from app import create_app
from models import db

BASE = "/api/v1/books"


class PaginationTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.client = self.app.test_client()
        for name, slug in [("Fiction", "fiction"), ("Technology", "technology")]:
            res = self.client.post("/api/v1/categories", json={"name": name, "slug": slug})
            self.assertEqual(res.status_code, 201, res.get_json())
        items = [
            ("Alpha", 50000, 1), ("Alpha", 50000, 1),
            ("Low", 30000, 1), ("High", 80000, 1),
            ("Tech Low", 30000, 2), ("Tech High", 90000, 2),
        ]
        for i, (title, price, cat) in enumerate(items, 1):
            res = self.client.post(BASE, json={
                "title": title, "isbn": f"97800000000{i:02d}",
                "price_vnd": price, "stock": i, "category_id": cat,
            })
            self.assertEqual(res.status_code, 201, res.get_json())

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get(self, args=""):
        return self.client.get(BASE + ("?" + args if args else ""))

    def assert_ids(self, response, ids):
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertEqual([book["id"] for book in response.get_json()["data"]], ids)

    def test_default_offset(self):
        res = self.get()
        self.assert_ids(res, [6, 5, 4, 3, 2, 1])
        self.assertEqual(res.get_json()["strategy"], "offset")
        self.assertEqual(res.get_json()["page"]["total"], 6)
        self.assertIsNone(res.get_json()["page"]["next"])

    def test_offset_first_middle_last(self):
        a = self.get("strategy=offset&genre=fiction&limit=2&sort=price,-title")
        self.assert_ids(a, [3, 1])
        self.assertTrue(a.get_json()["more"])
        self.assertEqual(a.get_json()["page"], {"offset": 0, "next": 2, "total": 4})
        b = self.get("strategy=offset&genre=fiction&limit=2&offset=2&sort=price,-title")
        self.assert_ids(b, [2, 4])
        self.assertFalse(b.get_json()["more"])
        self.assertIsNone(b.get_json()["page"]["next"])
        self.assert_ids(self.get("strategy=offset&offset=99"), [])

    def test_cursor_forward_without_skips_on_duplicates(self):
        args = "strategy=cursor&genre=fiction&sort=price,-title&limit=2"
        first = self.get(args)
        self.assert_ids(first, [3, 1])
        cursor = first.get_json()["page"]["next"]
        self.assertIsInstance(cursor, str)
        second = self.get(args + "&cursor=" + quote(cursor, safe=""))
        self.assert_ids(second, [2, 4])
        self.assertFalse(second.get_json()["more"])
        self.assertIsNone(second.get_json()["page"]["next"])

    def test_cursor_three_pages(self):
        args = "strategy=cursor&sort=-price&limit=2"
        observed = []
        cursor = None
        for _ in range(4):
            page = self.get(args + ("&cursor=" + quote(cursor, safe="") if cursor else ""))
            self.assertEqual(page.status_code, 200, page.get_json())
            observed.extend(item["id"] for item in page.get_json()["data"])
            cursor = page.get_json()["page"]["next"]
            if cursor is None:
                break
        self.assertEqual(observed, [6, 4, 1, 2, 3, 5])
        self.assertEqual(len(set(observed)), 6)

    def test_cursor_mixed_directions(self):
        args = "strategy=cursor&genre=fiction&sort=-price,title&limit=1"
        output = []
        cursor = None
        for _ in range(4):
            response = self.get(args + ("&cursor=" + quote(cursor, safe="") if cursor else ""))
            self.assertEqual(response.status_code, 200, response.get_json())
            output += [book["id"] for book in response.get_json()["data"]]
            cursor = response.get_json()["page"]["next"]
        self.assertEqual(output, [4, 1, 2, 3])
        self.assertIsNone(cursor)

    def test_sort_whitelist_and_multikey(self):
        self.assert_ids(self.get("sort=genre,-price,title&limit=20"), [4, 1, 2, 3, 6, 5])
        self.assert_ids(self.get("sort=title,-id&limit=20"), [2, 1, 4, 3, 6, 5])
        self.assert_ids(self.get("sort=id&limit=20"), [1, 2, 3, 4, 5, 6])

    def test_genre_filter(self):
        self.assert_ids(self.get("genre=technology&sort=price"), [5, 6])
        self.assert_ids(self.get("genre=none"), [])
        self.assertEqual(self.get("genre=none").get_json()["page"]["total"], 0)

    def test_invalid_strategy_and_numbers(self):
        cases = ["strategy=other", "limit=0", "limit=101", "limit=abc",
                 "offset=-1", "offset=1.1", "genre=", "genre=%3Cscript%3E"]
        for query in cases:
            with self.subTest(query=query):
                self.assertEqual(self.get(query).status_code, 400)

    def test_bad_sort(self):
        for s in ["foo", "price,-foo", "price,price", "price,", ",id", "--id", "id%3Bdrop", "-price,-price"]:
            with self.subTest(sort=s):
                res = self.get("sort=" + s)
                self.assertEqual(res.status_code, 400)
                self.assertEqual(res.get_json()["error"], "bad_sort")

    def test_cursor_errors(self):
        for c in ["invalid", "%25%25", "a" * 4100]:
            with self.subTest(cursor=c):
                self.assertEqual(self.get("strategy=cursor&cursor=" + c).status_code, 400)
        first = self.get("strategy=cursor&genre=fiction&sort=price&limit=2")
        token = quote(first.get_json()["page"]["next"], safe="")
        changed_sort = self.get("strategy=cursor&genre=fiction&sort=-price&cursor=" + token)
        self.assertEqual(changed_sort.status_code, 400)
        self.assertEqual(changed_sort.get_json()["error"], "sort_changed")
        changed_filter = self.get("strategy=cursor&genre=technology&sort=price&cursor=" + token)
        self.assertEqual(changed_filter.status_code, 400)
        self.assertEqual(changed_filter.get_json()["error"], "filter_changed")

    def test_does_not_mix_strategies(self):
        self.assertEqual(self.get("strategy=offset&cursor=bad").status_code, 400)
        self.assertEqual(self.get("strategy=cursor&offset=0").status_code, 400)

    def test_book_crud_is_preserved(self):
        res = self.client.get(BASE + "/1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["genre"], "fiction")
        updated = self.client.patch(BASE + "/1", json={"stock": 88})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.get_json()["stock"], 88)
        self.assertEqual(self.client.delete(BASE + "/1").status_code, 204)
        self.assert_ids(self.get("sort=id"), [2, 3, 4, 5, 6])

    def test_input_schema_rejects_invalid_book(self):
        bad = self.client.post(BASE, json={"title": "X"})
        self.assertEqual(bad.status_code, 400)


if __name__ == "__main__":
    unittest.main()
