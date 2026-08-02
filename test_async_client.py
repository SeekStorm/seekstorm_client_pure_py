"""Async end-to-end tests for the pure Python SeekStorm REST client.

Make sure the SeekStorm server is running before executing:
    python -m unittest -v test_async_client.py
"""

import os
import time
import unittest

try:
    # Installed package import
    from seekstorm_client import (
        ApikeyQuotaObject,
        AsyncSeekStorm,
        CreateIndexRequest,
        GetDocumentRequest,
        GetIteratorRequest,
        SearchRequestObject,
        UpdateDocumentRequest,
    )
except ImportError:
    # Local source import for this repository layout
    from src.seekstorm_client import (
        ApikeyQuotaObject,
        AsyncSeekStorm,
        CreateIndexRequest,
        GetDocumentRequest,
        GetIteratorRequest,
        SearchRequestObject,
        UpdateDocumentRequest,
    )


BASE_URL = os.getenv("SEEKSTORM_BASE_URL", "http://127.0.0.1:80")
DEMO_API_KEY = os.getenv(
    "SEEKSTORM_API_KEY",
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
)
MASTER_API_KEY = os.getenv(
    "SEEKSTORM_MASTER_API_KEY",
    "/iWStCpyfpd/BVlHOFtwnMgrFrmof4jGq/OQDWXQzcM=",
)


class TestAsyncSeekStormClientE2E(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncSeekStorm(base_url=BASE_URL, apikey_base64=DEMO_API_KEY)
        try:
            live = await self.client.live()
        except Exception as exc:  # pragma: no cover - runtime environment dependent
            self.skipTest(f"SeekStorm server not reachable at {BASE_URL}: {exc}")

        if "SeekStorm" not in live.message:
            self.skipTest(f"Unexpected live response: {live.message}")

    async def asyncTearDown(self):
        await self.client.close()

    def _build_schema(self):
        return [
            {"field": "title", "field_type": "Text", "store": True, "index_lexical": True},
            {
                "field": "body",
                "field_type": "Text",
                "store": True,
                "index_lexical": True,
                "longest": True,
            },
            {"field": "url", "field_type": "Text", "store": True, "index_lexical": False},
            {"field": "date", "field_type": "Timestamp", "store": True, "index_lexical": False},
        ]

    async def _create_test_index(self):
        request = CreateIndexRequest(
            index_name=f"e2e_async_{self._testMethodName}_{int(time.time() * 1000)}",
            schema=self._build_schema(),
            similarity="Bm25f",
            tokenizer="UnicodeAlphanumeric",
            stemmer="None",
            document_compression="Snappy",
            ngram_indexing=0,
        )
        return (await self.client.create_index(request)).index_id

    async def test_10_live(self):
        result = await self.client.live()
        self.assertIn("SeekStorm", result.message)

    async def test_20_create_and_delete_apikey_optional(self):
        if not MASTER_API_KEY:
            self.skipTest("SEEKSTORM_MASTER_API_KEY not set; skipping master-key endpoint test")

        quota = ApikeyQuotaObject(
            indices_max=10,
            indices_size_max=100_000_000_000,
            documents_max=100_000_000,
            operations_max=1_000_000_000,
            rate_limit=None,
            demo=False,
        )

        created = await self.client.create_apikey(MASTER_API_KEY, quota)
        self.assertTrue(created.api_key_base64)

        info = await self.client.get_apikey_info(apikey_base64=created.api_key_base64)
        self.assertIsNotNone(info.indices)

        deleted = await self.client.delete_apikey(created.api_key_base64, MASTER_API_KEY)
        self.assertGreaterEqual(deleted.remaining_api_keys, 0)

    async def test_30_index_lifecycle_end_to_end(self):
        index_id = await self._create_test_index()
        self.assertGreaterEqual(index_id, 0)

        try:
            info = await self.client.get_index_info(index_id)
            self.assertEqual(info.id, index_id)

            one_doc = {
                "title": "title-one",
                "body": "body one test marker",
                "url": "https://example.org/one",
                "date": 1730901447,
            }
            index_single = await self.client.index_document(index_id, one_doc)
            self.assertGreaterEqual(index_single.indexed_document_count, 0)

            many_docs = [
                {
                    "title": "title-two",
                    "body": "body two test",
                    "url": "https://example.org/two",
                    "date": 1730901448,
                },
                {
                    "title": "title-three",
                    "body": "body three test",
                    "url": "https://example.org/three",
                    "date": 1730901449,
                },
            ]
            index_bulk = await self.client.index_documents(index_id, many_docs)
            self.assertGreaterEqual(index_bulk.indexed_document_count, 0)

            committed = await self.client.commit_index(index_id)
            self.assertGreaterEqual(committed.indexed_document_count, 3)

            query_request = SearchRequestObject(
                query_string="+body +test",
                offset=0,
                length=10,
                enable_empty_query=False,
                realtime=False,
            )
            query_result = await self.client.query_index(index_id, query_request)
            self.assertGreaterEqual(query_result.count_total, 1)

            iterator_request = GetIteratorRequest(skip=0, take=10, include_document=True)
            iterator_result = await self.client.document_iterator(index_id, iterator_request)
            self.assertGreaterEqual(len(iterator_result.results), 1)

            doc_id = iterator_result.results[0].doc_id
            get_doc_request = GetDocumentRequest(query_terms=[], fields=[])
            got_doc = await self.client.get_document(index_id, doc_id, get_doc_request)
            self.assertIsInstance(got_doc.document, dict)
            self.assertGreaterEqual(len(got_doc.document), 1)

            updated_payload = {
                "title": "title-updated",
                "body": "body updated marker",
                "url": "https://example.org/updated",
                "date": 1730901450,
            }
            updated = await self.client.update_document(
                index_id,
                UpdateDocumentRequest(doc_id=doc_id, document=updated_payload),
            )
            self.assertGreaterEqual(updated.indexed_document_count, 1)

            deleted_single = await self.client.delete_document_by_docid(index_id, doc_id)
            self.assertGreaterEqual(deleted_single.indexed_document_count, 0)

            marker_doc = {
                "title": "title-delete-query",
                "body": "delete-query-marker",
                "url": "https://example.org/delete-query",
                "date": 1730901451,
            }
            await self.client.index_document(index_id, marker_doc)
            await self.client.commit_index(index_id)

            delete_query = SearchRequestObject(query_string="+delete-query-marker", length=10)
            deleted_by_query = await self.client.delete_documents_by_query(index_id, delete_query)
            self.assertGreaterEqual(deleted_by_query.indexed_document_count, 0)

            cleared = await self.client.clear_index(index_id)
            self.assertGreaterEqual(cleared.indexed_document_count, 0)

        finally:
            # Keep test runs idempotent even if an assertion fails in the middle.
            await self.client.delete_index(index_id)


if __name__ == "__main__":
    unittest.main(verbosity=2)
