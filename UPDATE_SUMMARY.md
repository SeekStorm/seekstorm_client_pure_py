# SeekStorm Python Client v0.2.0 Update Summary

## Overview
Updated the seekstorm-client-pure-py to align with upstream SeekStorm server API changes from v0.1.1 to v0.2.0.

## Changes Made

### 1. **New Dataclasses Added**

#### `DocumentOption` (seekstorm_client.py)
- **Purpose**: Consolidates document retrieval options (fields, highlights, distance_fields)
- **Location**: Line ~205
- **Attributes**:
  - `fields: List[str]` - Subset of document fields to return (empty = all fields)
  - `distance_fields: List[DistanceField]` - Vector distance configuration
  - `highlights: List[HighlightConfig]` - Highlight rules for text fields
- **Usage**: Used by `SearchRequestObject` and `GetDocumentRequest`

#### `IndexConfig` (seekstorm_client.py)
- **Purpose**: Separates index configuration from schema in `CreateIndexRequest`
- **Location**: Line ~299
- **Attributes**:
  - `name: str` (required) - Index name
  - `lexical_similarity: Optional[LexicalSimilarity]` (renamed from `similarity`)
  - `tokenizer: Optional[TokenizerType]`
  - `stemmer: Optional[StemmerType]`
  - `stop_words: Optional[StopwordType]`
  - `frequent_words: Optional[FrequentwordType]`
  - `ngram_indexing: Optional[NgramSet]`
  - `document_compression: Optional[DocumentCompression]`
  - `spelling_correction: Optional[SpellingCorrectionConfig]`
  - `query_completion: Optional[QueryCompletionConfig]`
  - `clustering: Optional[ClusteringConfig]`
  - `inference: Optional[InferenceConfig]`

### 2. **Modified Dataclasses**

#### `CreateIndexRequest` (seekstorm_client.py, Line ~335)
**Changes:**
- **Removed fields**: `index_name`, `similarity`, `tokenizer`, `stemmer`, `stop_words`, `frequent_words`, `ngram_indexing`, `document_compression`, `spelling_correction`, `query_completion`, `clustering`, `inference`
- **Added fields**: `index_config: IndexConfig` (required, replaces `index_name` and all config options)
- **Changed serialization**: Updated `to_payload()` to properly serialize `index_config`
- **Kept fields**: `schema`, `synonyms`

#### `SearchRequestObject` (seekstorm_client.py, Line ~426)
**Changes:**
- **Removed fields**: `fields`, `highlights`, `distance_fields`
- **Added field**: `return_documents: Optional[DocumentOption]`
- **Behavior**: 
  - When `return_documents=None`, documents are not returned
  - When `return_documents=DocumentOption()`, returns all stored fields (default)
  - When `return_documents=DocumentOption(fields=[...])`, returns specified fields

#### `GetDocumentRequest` (seekstorm_client.py, Line ~408)
**Changes:**
- **Removed fields**: `fields`, `highlights`, `distance_fields`
- **Added field**: `return_documents: Optional[DocumentOption]`
- **Behavior**: Same as `SearchRequestObject`

### 3. **Updated Test Files**

#### test_client.py (Synchronous Tests)
- Updated imports to include `DocumentOption` and `IndexConfig`
- Changed `_create_test_index()` to use new `CreateIndexRequest` structure
- Updated `get_doc_request` to use `return_documents` parameter

#### test_async_client.py (Asynchronous Tests)
- Updated imports to include `DocumentOption` and `IndexConfig`
- Changed async `_create_test_index()` to use new `CreateIndexRequest` structure
- Updated `get_doc_request` to use `return_documents` parameter

### 4. **Updated Documentation**

#### README.md
- Updated "Quick Start (Sync)" example with new API
- Updated "Quick Start (Async)" example with new API
- Added `DocumentOption` and `IndexConfig` to dataclass list

#### MIGRATION_GUIDE.md (New)
- Comprehensive migration guide from v0.1.1 → v0.2.0
- Before/after code examples for all breaking changes
- Detailed explanation of each change
- Common usage patterns

#### CHANGELOG.md
- Added v0.2.0 section with all breaking changes
- Documented added features
- Noted renamed fields (similarity → lexical_similarity)

### 5. **Public API Updates**

#### src/__init__.py
- Added exports: `DocumentOption`, `IndexConfig`
- Updated `__all__` list to include new types

### 6. **Field Renames**
- `CreateIndexRequest.similarity` → `IndexConfig.lexical_similarity`
  - This aligns with Rust server API where the field is `lexical_similarity`

## Migration Path for Users

### CreateIndexRequest
```python
# Old (v0.1.1)
CreateIndexRequest(
    index_name="demo",
    similarity="Bm25f",
    tokenizer="UnicodeAlphanumeric",
    schema=[...],
)

# New (v0.2.0)
CreateIndexRequest(
    index_config=IndexConfig(
        name="demo",
        lexical_similarity="Bm25f",
        tokenizer="UnicodeAlphanumeric",
    ),
    schema=[...],
)
```

### SearchRequestObject
```python
# Old (v0.1.1)
SearchRequestObject(
    query_string="test",
    fields=["title"],
    highlights=[{"field": "body"}],
)

# New (v0.2.0)
SearchRequestObject(
    query_string="test",
    return_documents=DocumentOption(
        fields=["title"],
        highlights=[{"field": "body"}],
    ),
)
```

### GetDocumentRequest
```python
# Old (v0.1.1)
GetDocumentRequest(
    query_terms=["test"],
    fields=["title"],
    highlights=[...],
)

# New (v0.2.0)
GetDocumentRequest(
    query_terms=["test"],
    return_documents=DocumentOption(
        fields=["title"],
        highlights=[...],
    ),
)
```

## Testing
- All changes verified with comprehensive test script
- Test files updated and compatible with new API
- No changes to client methods (SeekStorm, AsyncSeekStorm)
- Backward compatibility not maintained (breaking change release v0.2.0)

## Files Modified
1. `src/seekstorm_client.py` - Core changes to dataclasses
2. `src/__init__.py` - Export new types
3. `test_client.py` - Update sync tests
4. `test_async_client.py` - Update async tests
5. `README.md` - Update examples
6. `CHANGELOG.md` - Document changes
7. `MIGRATION_GUIDE.md` - New migration guide

## Compatibility
- **Breaking Changes**: Yes (v0.2.0 is a major version bump)
- **Python Version**: No changes to minimum Python version
- **Dependencies**: No new dependencies
- **Server Compatibility**: Requires SeekStorm server with new API

## Alignment with Upstream
These changes align the Python client with the upstream SeekStorm Rust server API where:
1. `SearchRequest` uses `return_documents: Option<DocumentOption>`
2. `CreateIndexRequest` contains `index_config: IndexConfig` and schema
3. All optional fields in `IndexConfig` use Rust Option type (None in Python)
