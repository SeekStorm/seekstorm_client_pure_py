# Migration Guide v0.1.1 → v0.2.0

This guide describes the breaking changes in version 0.2.0 and how to migrate your code.

## CreateIndexRequest Changes

The `CreateIndexRequest` has been restructured to separate index configuration from schema definition.

### Before (v0.1.1)
```python
from seekstorm_client import CreateIndexRequest

request = CreateIndexRequest(
    index_name="demo_index",
    schema=[
        {"field": "title", "field_type": "Text", "store": True, "index_lexical": True},
        {"field": "body", "field_type": "Text", "store": True, "index_lexical": True},
    ],
    similarity="Bm25f",
    tokenizer="UnicodeAlphanumeric",
    stemmer="None",
    document_compression="Snappy",
    ngram_indexing=0,
)
```

### After (v0.2.0)
```python
from seekstorm_client import CreateIndexRequest, IndexConfig

request = CreateIndexRequest(
    index_config=IndexConfig(
        name="demo_index",
        lexical_similarity="Bm25f",
        tokenizer="UnicodeAlphanumeric",
        stemmer="None",
        document_compression="Snappy",
        ngram_indexing=0,
    ),
    schema=[
        {"field": "title", "field_type": "Text", "store": True, "index_lexical": True},
        {"field": "body", "field_type": "Text", "store": True, "index_lexical": True},
    ],
)
```

### Key Changes
- `index_name` → `index_config.name`
- `similarity` → `index_config.lexical_similarity`
- All other config fields moved to `IndexConfig`: `tokenizer`, `stemmer`, `stop_words`, `frequent_words`, `ngram_indexing`, `document_compression`, `spelling_correction`, `query_completion`, `clustering`, `inference`
- `schema` and `synonyms` remain at the top level of `CreateIndexRequest`

## SearchRequestObject Changes

The fields controlling document retrieval have been consolidated into a new `DocumentOption` object.

### Before (v0.1.1)
```python
from seekstorm_client import SearchRequestObject

query = SearchRequestObject(
    query_string="+hello +seekstorm",
    offset=0,
    length=10,
    fields=["title", "body"],
    highlights=[{"field": "body", "fragment_size": 150}],
    distance_fields=[],
)
```

### After (v0.2.0)
```python
from seekstorm_client import SearchRequestObject, DocumentOption

query = SearchRequestObject(
    query_string="+hello +seekstorm",
    offset=0,
    length=10,
    return_documents=DocumentOption(
        fields=["title", "body"],
        highlights=[{"field": "body", "fragment_size": 150}],
        distance_fields=[],
    ),
)
```

### Key Changes
- Removed: `fields`, `highlights`, `distance_fields` attributes
- Added: `return_documents: Optional[DocumentOption]` attribute
- All document retrieval options are now nested in `DocumentOption`
- If you don't want to return any documents, set `return_documents=None`
- If you want all documents with all fields (default), use `DocumentOption()` or `DocumentOption(fields=[])`

## GetDocumentRequest Changes

Similar consolidation as `SearchRequestObject`.

### Before (v0.1.1)
```python
from seekstorm_client import GetDocumentRequest

request = GetDocumentRequest(
    query_terms=["hello", "seekstorm"],
    fields=["title", "body"],
    highlights=[{"field": "body"}],
    distance_fields=[],
)
```

### After (v0.2.0)
```python
from seekstorm_client import GetDocumentRequest, DocumentOption

request = GetDocumentRequest(
    query_terms=["hello", "seekstorm"],
    return_documents=DocumentOption(
        fields=["title", "body"],
        highlights=[{"field": "body"}],
        distance_fields=[],
    ),
)
```

### Key Changes
- Removed: `fields`, `highlights`, `distance_fields` attributes
- Added: `return_documents: Optional[DocumentOption]` attribute
- All document retrieval options are now nested in `DocumentOption`

## New Dataclass: DocumentOption

The new `DocumentOption` dataclass consolidates all document retrieval options:

```python
from seekstorm_client import DocumentOption

# Return only title and body fields with highlights
doc_option = DocumentOption(
    fields=["title", "body"],
    highlights=[
        {"field": "title", "name": "query_highlight"},
        {"field": "body", "fragment_size": 150},
    ],
    distance_fields=[
        {"field": "embedding", "metric": "cosine", "top_k": 5}
    ],
)

# Return all fields (default behavior when empty)
doc_option = DocumentOption()

# Return no documents (for count-only queries)
# Set return_documents=None in SearchRequestObject
```

## New Dataclass: IndexConfig

The new `IndexConfig` dataclass contains all index configuration options:

```python
from seekstorm_client import IndexConfig

config = IndexConfig(
    name="my_index",
    lexical_similarity="Bm25f",
    tokenizer="UnicodeAlphanumeric",
    stemmer="English",
    stop_words="English",
    frequent_words="English",
    ngram_indexing=9,
    document_compression="Snappy",
    spelling_correction=None,
    query_completion=None,
    clustering=None,
    inference=None,
)
```

All configuration fields except `name` are optional and will use server defaults if not specified.
