# SeekStorm Pure Python REST Client

<img src="assets/logo.png" width="450" alt="Logo"><br>
**Pure Python REST client**, using `httpx` (sync and async), for the **SeekStorm vector & lexical search server**.

seekstorm_client_pure_py is open source licensed under the [Apache License 2.0](https://github.com/SeekStorm/seekstorm_client_py?tab=Apache-2.0-1-ov-file#readme)

## SeekStorm REST client (Pure Python)
[![PyPI](https://img.shields.io/pypi/v/seekstorm-client-pure-py?label=PyPI)](https://pypi.org/project/seekstorm-client-pure-py/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/seekstorm_client_pure_py?tab=Apache-2.0-1-ov-file#readme)

## SeekStorm REST client (Python wrapper via PyO3/Maturin)
[![PyPI](https://img.shields.io/pypi/v/seekstorm-client-py?label=PyPI)](https://pypi.org/project/seekstorm-client-py/)
[![GitHub Stars](https://img.shields.io/github/stars/SeekStorm/seekstorm_client_py)](https://github.com/SeekStorm/seekstorm_client_py)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/seekstorm_client_py?tab=Apache-2.0-1-ov-file#readme)

## SeekStorm REST client (C#)
[![NuGet version](https://badge.fury.io/nu/symspell.svg)](https://badge.fury.io/nu/seekstorm_client_cs)
[![GitHub Stars](https://img.shields.io/github/stars/SeekStorm/seekstorm_client_cs)](https://github.com/SeekStorm/seekstorm_client_cs)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/seekstorm_client_cs?tab=Apache-2.0-1-ov-file#readme)

## SeekStorm REST client (Rust)
[![Crates.io](https://img.shields.io/crates/v/seekstorm_client_rs.svg)](https://crates.io/crates/seekstorm_client_rs)
[![Downloads](https://img.shields.io/crates/d/seekstorm_client_rs.svg?style=flat-square)](https://crates.io/crates/seekstorm_client_rs)
[![Documentation](https://docs.rs/seekstorm_client_rs/badge.svg)](https://docs.rs/seekstorm_client_rs)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/SeekStorm?tab=Apache-2.0-1-ov-file#readme)
[![Roadmap](https://img.shields.io/badge/Roadmap-2026-DA7F07.svg)](#roadmap)

## SeekStorm multi-tenancy search server
[![Crates.io](https://img.shields.io/crates/v/seekstorm_server.svg)](https://crates.io/crates/seekstorm_server)
[![Downloads](https://img.shields.io/crates/d/seekstorm_server.svg?style=flat-square)](https://crates.io/crates/seekstorm_server)
[![Docker](https://img.shields.io/docker/pulls/wolfgarbe/seekstorm_server)](https://hub.docker.com/r/wolfgarbe/seekstorm_server)
[![REST API Documentation](https://docs.rs/seekstorm/badge.svg)](https://seekstorm.github.io/documentation/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/SeekStorm?tab=Apache-2.0-1-ov-file#readme)
[![Roadmap](https://img.shields.io/badge/Roadmap-2026-DA7F07.svg)](#roadmap)

## SeekStorm in-process search library
[![Crates.io](https://img.shields.io/crates/v/seekstorm.svg)](https://crates.io/crates/seekstorm)
[![Downloads](https://img.shields.io/crates/d/seekstorm.svg?style=flat-square)](https://crates.io/crates/seekstorm)
[![Documentation](https://docs.rs/seekstorm/badge.svg)](https://docs.rs/seekstorm)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/SeekStorm/SeekStorm?tab=Apache-2.0-1-ov-file#readme)
[![Roadmap](https://img.shields.io/badge/Roadmap-2026-DA7F07.svg)](#roadmap)
<p>
  <a href="https://seekstorm.com">Website</a> | 
  <a href="https://seekstorm.github.io/search-benchmark-game/">Benchmark</a> | 
  <a href="https://deephn.org/">Demo</a> | 
  <a href="https://github.com/SeekStorm/seekstorm_client_py">Repository for SeekStorm Python client </a> | 
  <a href="https://github.com/SeekStorm/SeekStorm">Repository for SeekStorm library, server, Rust client </a> | 
  <a href="https://github.com/SeekStorm/SeekStorm#roadmap">Roadmap</a> | 
  <a href="https://seekstorm.com/blog/">Blog</a> | 
  <a href="https://x.com/seekstorm">X</a>
</p>


## Install

```shell
pip install seekstorm-client-pure-py
```

## Quick Start (Sync)

```python
from seekstorm_client import (
  SeekStorm,
  CreateIndexRequest,
  SearchRequestObject,
)

BASE_URL = "http://127.0.0.1:80"
DEMO_API_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="

client = SeekStorm(base_url=BASE_URL, apikey_base64=DEMO_API_KEY)

schema = [
  {"field": "title", "field_type": "Text", "store": True, "index_lexical": True},
  {"field": "body", "field_type": "Text", "store": True, "index_lexical": True, "longest": True},
  {"field": "url", "field_type": "Text", "store": True, "index_lexical": False},
]

create_request = CreateIndexRequest(
  index_name="demo_index",
  schema=schema,
  similarity="Bm25f",
  tokenizer="UnicodeAlphanumeric",
  stemmer="None",
  document_compression="Snappy",
  ngram_indexing=0,
)

index_id = client.create_index(create_request).index_id

client.index_document(index_id, {"title": "title1", "body": "hello seekstorm", "url": "https://example.org"})
client.commit_index(index_id)

query = SearchRequestObject(query_string="+hello +seekstorm", offset=0, length=10)
result = client.query_index(index_id, query)

print(result.count_total)
client.delete_index(index_id)
client.close()
```

## Quick Start (Async)

```python
import asyncio

from seekstorm_client import AsyncSeekStorm, CreateIndexRequest, SearchRequestObject


async def main() -> None:
  client = AsyncSeekStorm(base_url="http://127.0.0.1:80", apikey_base64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")

  request = CreateIndexRequest(
    index_name="demo_async_index",
    schema=[
      {"field": "title", "field_type": "Text", "store": True, "index_lexical": True},
      {"field": "body", "field_type": "Text", "store": True, "index_lexical": True},
    ],
  )

  index_id = (await client.create_index(request)).index_id

  await client.index_document(index_id, {"title": "async", "body": "hello"})
  await client.commit_index(index_id)

  result = await client.query_index(index_id, SearchRequestObject(query_string="+hello"))
  print(result.count_total)

  await client.delete_index(index_id)
  await client.close()


asyncio.run(main())
```

## Dataclasses

The client exposes typed dataclasses for common request/response objects.

Request dataclasses:

- `ApikeyQuotaObject`
- `CreateIndexRequest`
- `DeleteApikeyRequest`
- `GetDocumentRequest`
- `GetIteratorRequest`
- `SearchRequestObject`
- `UpdateDocumentRequest`
- `UpdateDocumentsRequest`

Response dataclasses:

- `LiveResponse`
- `ApiKeyResponse`
- `RemainingApiKeysResponse`
- `ApikeyInfoResponse`
- `CreateIndexResponse`
- `RemainingIndicesResponse`
- `IndexedDocumentCountResponse`
- `IndexResponseObject`
- `IteratorResultItem`
- `IteratorResult`
- `DocumentResponse`
- `PdfResponse`
- `SearchResultObject`

Error type:

- `SeekStormApiError` (contains `status_code` and `body`)

## API Key Endpoints

The client supports API key lifecycle endpoints, including `create_apikey`.

REST routes:

- `POST /api/v1/apikey` -> `create_apikey(...)`
- `GET /api/v1/apikey` -> `get_apikey_info(...)`
- `DELETE /api/v1/apikey` -> `delete_apikey(...)`

Sync example:

```python
from seekstorm_client import SeekStorm, ApikeyQuotaObject

client = SeekStorm(base_url="http://127.0.0.1:80")
master_key = "/iWStCpyfpd/BVlHOFtwnMgrFrmof4jGq/OQDWXQzcM="

quota = ApikeyQuotaObject(
  indices_max=10,
  indices_size_max=100_000_000_000,
  documents_max=100_000_000,
  operations_max=1_000_000_000,
  rate_limit=None,
  demo=True,
)

created = client.create_apikey(master_key, quota)
print(created.api_key_base64)

info = client.get_apikey_info(apikey_base64=created.api_key_base64)
print(len(info.indices))

remaining = client.delete_apikey(created.api_key_base64, master_key)
print(remaining.remaining_api_keys)

client.close()
```

## Method Signatures

### Sync client: `SeekStorm`

```python
SeekStorm(base_url: str, apikey_base64: str | None = None, timeout: float = 30.0)
```

All endpoint methods accept an optional `base_url: str | None = None` parameter to override the client default host for that single request.

API key endpoints:

- `live() -> LiveResponse`
- `create_apikey(master_apikey: str, api_key_quota_object: ApikeyQuotaObject) -> ApiKeyResponse`
- `delete_apikey(apikey_base64: str, master_apikey_base64: str) -> RemainingApiKeysResponse`
- `get_apikey_info(apikey_base64: str | None = None) -> ApikeyInfoResponse`

Index endpoints:

- `create_index(request: CreateIndexRequest, apikey_base64: str | None = None) -> CreateIndexResponse`
- `delete_index(index_id: int, apikey_base64: str | None = None) -> RemainingIndicesResponse`
- `clear_index(index_id: int, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `commit_index(index_id: int, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `get_index_info(index_id: int, apikey_base64: str | None = None) -> IndexResponseObject`

Document endpoints:

- `index_document(index_id: int, document: dict, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `index_documents(index_id: int, documents: Sequence[dict], apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `index_pdf(index_id: int, file_path: str | Path, file_date: int, document: bytes, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `get_pdf(index_id: int, doc_id: int, apikey_base64: str | None = None) -> PdfResponse`
- `get_document(index_id: int, doc_id: int, request: GetDocumentRequest, apikey_base64: str | None = None) -> DocumentResponse`
- `update_document(index_id: int, request: UpdateDocumentRequest, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `update_documents(index_id: int, request: UpdateDocumentsRequest, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `delete_document_by_docid(index_id: int, doc_id: int, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `delete_documents_by_docid(index_id: int, doc_id_vec: Sequence[int], apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `delete_documents_by_query(index_id: int, query: SearchRequestObject, apikey_base64: str | None = None) -> IndexedDocumentCountResponse`
- `document_iterator(index_id: int, request: GetIteratorRequest, apikey_base64: str | None = None) -> IteratorResult`
- `query_index(index_id: int, request: SearchRequestObject, apikey_base64: str | None = None) -> SearchResultObject`

### Async client: `AsyncSeekStorm`

`AsyncSeekStorm` exposes the same endpoint methods as `SeekStorm`, but all methods are `async` and must be awaited.

## Tests

Make sure the SeekStorm server is running before running tests.

Optional environment variables:

- `SEEKSTORM_BASE_URL` (default: `http://127.0.0.1:80`)
- `SEEKSTORM_API_KEY` (default: demo key)
- `SEEKSTORM_MASTER_API_KEY` (default in tests is set to the known local dev master key)

Run sync tests:

```shell
python -m unittest -v test_client.py
```

Run async tests:

```shell
python -m unittest -v test_async_client.py
```

Run both suites in one command:

```shell
python -m unittest -v test_client.py test_async_client.py
```