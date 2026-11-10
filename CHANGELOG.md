# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-10

### Changed

- **BREAKING**: `SearchRequestObject` now uses `return_documents: Optional[DocumentOption]` instead of separate `fields`, `highlights`, and `distance_fields` attributes
- **BREAKING**: `GetDocumentRequest` now uses `return_documents: Optional[DocumentOption]` instead of separate `fields`, `highlights`, and `distance_fields` attributes
- **BREAKING**: `CreateIndexRequest` restructured to split configuration into separate `IndexConfig` dataclass, which is now a required `index_config` parameter
  - Old: `CreateIndexRequest(index_name="demo", similarity="Bm25f", tokenizer="UnicodeAlphanumeric", ...)`
  - New: `CreateIndexRequest(index_config=IndexConfig(name="demo", lexical_similarity="Bm25f", tokenizer="UnicodeAlphanumeric", ...), schema=...)`
- **BREAKING**: `SearchResultObject` restructured to separate result metadata from documents
  - `results` field now contains `List[SearchResult]` (doc_id and score only), always returned
  - New `documents` field contains `List[Document]` (full documents), only returned if `return_documents` was specified
  - Renamed field in `IndexConfig`: `similarity` → `lexical_similarity` for consistency with the server API

### Added

- New `DocumentOption` dataclass for controlling document retrieval in search and get_document requests
- New `IndexConfig` dataclass for index configuration parameters
- New `SearchResult` TypedDict for individual search results (doc_id and score)
- New fields in `SearchResultObject`: `documents`, `observed_vector_count`, `observed_cluster_count`
- `DocumentOption`, `IndexConfig`, and `SearchResult` are now exported in public API

## [0.1.1] - 2026-08-04

### Added

- documentation comments and IntelliSense guidance added

## [0.1.0] - 2026-07-30

### Added

- Initial release of the Python client library/SDK for the SeekStorm server REST API
