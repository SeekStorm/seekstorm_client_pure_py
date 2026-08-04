"""A pure-python REST client for SeekStorm search engine."""

from __future__ import annotations

__version__ = "0.1.0"

from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

import httpx


Document = Dict[str, Any]

# Rust ground-truth enum names from seekstorm_client/src/lib.rs:
# LexicalSimilarity, TokenizerType, StemmerType, StopwordType, FrequentwordType,
# DocumentCompression, ResultType, QueryType, QueryRewriting, SearchMode, NgramSet.
#
# NgramSet in SeekStorm is a bitmask enum (flags), therefore `int` remains the correct
# representation for single flags and bitwise combinations.
LexicalSimilarity = Literal["Bm25f", "Bm25fProximity"]
TokenizerType = Literal[
    "AsciiAlphabetic",
    "UnicodeAlphanumeric",
    "UnicodeAlphanumericFolded",
    "Whitespace",
    "WhitespaceLowercase",
    "UnicodeAlphanumericZH",
]
StemmerType = Literal[
    "None",
    "Arabic",
    "Armenian",
    "Basque",
    "Catalan",
    "Czech",
    "Danish",
    "Dutch",
    "DutchPorter",
    "English",
    "Esperanto",
    "Estonian",
    "Finnish",
    "French",
    "German",
    "Greek",
    "Hindi",
    "Hungarian",
    "Indonesian",
    "Irish",
    "Italian",
    "Lithuanian",
    "Lovins",
    "Nepali",
    "Norwegian",
    "Persian",
    "Polish",
    "Porter",
    "Portuguese",
    "Romanian",
    "Russian",
    "Serbian",
    "Sesotho",
    "Spanish",
    "Swedish",
    "Tamil",
    "Turkish",
    "Ukrainian",
    "Yiddish",
]
StopwordSimple = Literal["None", "English", "German", "French", "Spanish"]
StopwordCustom = Dict[Literal["Custom"], Dict[Literal["terms"], List[str]]]
StopwordType = Union[StopwordSimple, StopwordCustom]
FrequentwordSimple = Literal["None", "English", "German", "French", "Spanish"]
FrequentwordCustom = Dict[Literal["Custom"], Dict[Literal["terms"], List[str]]]
FrequentwordType = Union[FrequentwordSimple, FrequentwordCustom]
DocumentCompression = Literal["None", "Lz4", "Snappy", "Zstd"]
NgramSet = int
ResultType = Literal["Count", "Topk", "TopkCount"]
QueryType = Literal["Union", "Intersection", "Phrase", "Not"]
QueryRewritingConfig = Dict[str, Any]
QueryRewriting = Union[
    Literal["SearchOnly"],
    Dict[Literal["SearchSuggest"], QueryRewritingConfig],
    Dict[Literal["SearchRewrite"], QueryRewritingConfig],
    Dict[Literal["SuggestOnly"], QueryRewritingConfig],
]
SearchModeConfig = Dict[str, Any]
SearchMode = Union[
    Literal["Lexical"],
    Dict[Literal["Vector"], SearchModeConfig],
    Dict[Literal["Hybrid"], SearchModeConfig],
]


class SeekStormApiError(Exception):
    """HTTP/API error returned by the SeekStorm server."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"SeekStorm API error {status_code}: {body}")


@dataclass
class LiveResponse:
    """Response returned by the health endpoint.

    Attributes:
        message: Raw response text returned by the SeekStorm live endpoint.
    """

    message: str


@dataclass
class ApiKeyResponse:
    """Response returned when creating a new API key.

    Attributes:
        api_key_base64: Newly generated API key in base64 representation.
    """

    api_key_base64: str


@dataclass
class RemainingApiKeysResponse:
    """Response returned after deleting an API key.

    Attributes:
        remaining_api_keys: Number of API keys still available for creation.
    """

    remaining_api_keys: int


@dataclass
class ApikeyQuotaObject:
    """Quota and feature limits assigned to an API key.

    Attributes:
        indices_max: Maximum number of indices allowed for the API key.
        indices_size_max: Maximum combined index size in bytes.
        documents_max: Maximum number of indexed documents.
        operations_max: Maximum number of indexing operations.
        rate_limit: Optional per-minute or per-window request limit configured server-side.
        demo: Whether demo restrictions should be enabled for this API key.
    """

    indices_max: int = 0
    indices_size_max: int = 0
    documents_max: int = 0
    operations_max: int = 0
    rate_limit: Optional[int] = None
    demo: bool = False


@dataclass
class DeleteApikeyRequest:
    """Request payload to delete an existing API key.

    Attributes:
        apikey_base64: API key to be removed.
    """

    apikey_base64: str


@dataclass
class CreateIndexRequest:
    """Request payload to create a new index.

    Attributes:
        index_name: Human-readable name of the index.
        schema: Field schema definition for indexed document fields.
        similarity: Lexical similarity algorithm used for scoring.
        tokenizer: Tokenizer strategy applied during indexing and search.
        stemmer: Stemmer configuration for term normalization.
        stop_words: Stop-word handling mode.
        frequent_words: Frequent-word handling mode.
        ngram_indexing: N-gram indexing mode/level.
        document_compression: Document storage compression setting.
        synonyms: Synonym rules used for query expansion.
        spelling_correction: Spelling correction configuration object.
        query_completion: Query completion/autocomplete configuration object.
        clustering: Result clustering configuration object.
        inference: Vector inference configuration object.
    """

    index_name: str
    schema: List[Dict[str, Any]] = field(default_factory=list)
    similarity: Optional[LexicalSimilarity] = None
    tokenizer: Optional[TokenizerType] = None
    stemmer: Optional[StemmerType] = None
    stop_words: Optional[StopwordType] = None
    frequent_words: Optional[FrequentwordType] = None
    ngram_indexing: Optional[NgramSet] = None
    document_compression: Optional[DocumentCompression] = None
    synonyms: List[Dict[str, Any]] = field(default_factory=list)
    spelling_correction: Optional[Dict[str, Any]] = None
    query_completion: Optional[Dict[str, Any]] = None
    clustering: Optional[Dict[str, Any]] = None
    inference: Optional[Dict[str, Any]] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "index_name": self.index_name,
            "schema": self.schema,
        }

        optional_values = {
            "similarity": self.similarity,
            "tokenizer": self.tokenizer,
            "stemmer": self.stemmer,
            "stop_words": self.stop_words,
            "frequent_words": self.frequent_words,
            "ngram_indexing": self.ngram_indexing,
            "document_compression": self.document_compression,
            "spelling_correction": self.spelling_correction,
            "query_completion": self.query_completion,
            "clustering": self.clustering,
            "inference": self.inference,
        }

        for key, value in optional_values.items():
            if value is not None:
                payload[key] = value

        if self.synonyms:
            payload["synonyms"] = self.synonyms

        return payload


@dataclass
class GetIteratorRequest:
    """Request payload for document iteration.

    Attributes:
        document_id: Optional anchor document id used as starting position.
        skip: Number of items to skip from the anchor.
        take: Number of items to return.
        include_deleted: Whether soft-deleted documents should be included.
        include_document: Whether full document bodies should be included.
        fields: Optional subset of document fields to include.
    """

    document_id: Optional[int] = None
    skip: int = 0
    take: int = 1
    include_deleted: bool = False
    include_document: bool = False
    fields: List[str] = field(default_factory=list)


@dataclass
class GetDocumentRequest:
    """Request payload for retrieving a document with query-aware decorations.

    Attributes:
        query_terms: Query terms used for highlight and scoring context.
        highlights: Highlight rules applied to text fields.
        fields: Optional subset of document fields to return.
        distance_fields: Distance/similarity configuration for vector-aware fields.
    """

    query_terms: List[str] = field(default_factory=list)
    highlights: List[Dict[str, Any]] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    distance_fields: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SearchRequestObject:
    """Request payload for querying an index.

    Attributes:
        query_string: Search query string. Serialized as `query` in the REST payload.
        query_vector: Optional vector used for semantic or hybrid search.
        enable_empty_query: Whether empty queries are allowed.
        offset: Zero-based starting offset for paging.
        length: Number of hits to return.
        result_type: Result mode, for example top-k only vs top-k with count.
        realtime: Whether to include uncommitted changes.
        highlights: Highlighting configuration entries.
        field_filter: Field-level filters for query execution.
        fields: Subset of fields to return for each hit.
        distance_fields: Distance/similarity configuration entries.
        query_facets: Facet aggregation requests.
        facet_filter: Facet filters applied before returning results.
        result_sort: Explicit sorting instructions.
        query_type_default: Default boolean query type.
        query_rewriting: Query rewriting behavior.
        search_mode: Lexical/vector/hybrid mode.
    """

    query_string: str
    query_vector: Optional[Any] = None
    enable_empty_query: bool = False
    offset: int = 0
    length: int = 10
    result_type: ResultType = "TopkCount"
    realtime: bool = False
    highlights: List[Dict[str, Any]] = field(default_factory=list)
    field_filter: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    distance_fields: List[Dict[str, Any]] = field(default_factory=list)
    query_facets: List[Dict[str, Any]] = field(default_factory=list)
    facet_filter: List[Dict[str, Any]] = field(default_factory=list)
    result_sort: List[Dict[str, Any]] = field(default_factory=list)
    query_type_default: QueryType = "Intersection"
    query_rewriting: QueryRewriting = "SearchOnly"
    search_mode: SearchMode = "Lexical"

    def to_payload(self) -> Dict[str, Any]:
        payload = _to_payload_from_dataclass(self)
        payload["query"] = payload.pop("query_string")
        return payload


@dataclass
class UpdateDocumentRequest:
    """Request payload for updating a single document.

    Attributes:
        doc_id: Internal SeekStorm document id to update.
        document: Partial or full replacement document content.
    """

    doc_id: int
    document: Document

    def to_payload(self) -> List[Any]:
        return [self.doc_id, self.document]


@dataclass
class UpdateDocumentsRequest:
    """Request payload for batch document updates.

    Attributes:
        items: Sequence of single-document update operations.
    """

    items: List[UpdateDocumentRequest]

    def to_payload(self) -> List[List[Any]]:
        return [item.to_payload() for item in self.items]


@dataclass
class CreateIndexResponse:
    """Response returned after index creation.

    Attributes:
        index_id: Numeric identifier of the newly created index.
    """

    index_id: int


@dataclass
class RemainingIndicesResponse:
    """Response returned after index deletion.

    Attributes:
        remaining_indices: Number of indices still available for creation.
    """

    remaining_indices: int


@dataclass
class IndexedDocumentCountResponse:
    """Response containing the current indexed document count.

    Attributes:
        indexed_document_count: Number of documents currently indexed.
    """

    indexed_document_count: int


@dataclass
class IndexResponseObject:
    """Metadata returned for a SeekStorm index.

    Attributes:
        id: Index identifier.
        name: Index name.
        schema: Effective index schema keyed by field name.
        indexed_doc_count: Number of indexed (including pending) documents.
        committed_doc_count: Number of committed documents.
        operations_count: Total write operations applied to the index.
        query_count: Total executed queries.
        version: SeekStorm index version string.
        facets_minmax: Per-facet min/max statistics if available.
    """

    id: int
    name: str
    schema: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    indexed_doc_count: int = 0
    committed_doc_count: int = 0
    operations_count: int = 0
    query_count: int = 0
    version: str = ""
    facets_minmax: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexResponseObject":
        return cls(
            id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            schema=dict(data.get("schema", {}) or {}),
            indexed_doc_count=int(data.get("indexed_doc_count", 0)),
            committed_doc_count=int(data.get("committed_doc_count", 0)),
            operations_count=int(data.get("operations_count", 0)),
            query_count=int(data.get("query_count", 0)),
            version=str(data.get("version", "")),
            facets_minmax=dict(data.get("facets_minmax", {}) or {}),
        )


@dataclass
class ApikeyInfoResponse:
    """Response containing API-key-visible index metadata.

    Attributes:
        indices: List of indices accessible with the queried API key.
    """

    indices: List[IndexResponseObject] = field(default_factory=list)


def _parse_apikey_info_payload(payload: Any) -> ApikeyInfoResponse:
    """Parse apikey info payload across server response variants."""
    if isinstance(payload, list):
        return ApikeyInfoResponse(
            indices=[IndexResponseObject.from_dict(item) for item in payload if isinstance(item, dict)]
        )

    if isinstance(payload, dict):
        for key in ("indices", "result", "Ok", "ok", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return ApikeyInfoResponse(
                    indices=[IndexResponseObject.from_dict(item) for item in value if isinstance(item, dict)]
                )
        if all(field in payload for field in ("id", "name")):
            return ApikeyInfoResponse(indices=[IndexResponseObject.from_dict(payload)])

    return ApikeyInfoResponse(indices=[])


@dataclass
class IteratorResultItem:
    """Single item returned by the document iterator endpoint.

    Attributes:
        doc_id: Internal SeekStorm document id.
        doc: Optional materialized document payload.
    """

    doc_id: int
    doc: Optional[Document] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IteratorResultItem":
        return cls(doc_id=int(data.get("doc_id", 0)), doc=data.get("doc"))


@dataclass
class IteratorResult:
    """Document iterator response page.

    Attributes:
        skip: Number of skipped items reflected in this result.
        results: Iterator items returned for the request window.
    """

    skip: int
    results: List[IteratorResultItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IteratorResult":
        return cls(
            skip=int(data.get("skip", 0)),
            results=[IteratorResultItem.from_dict(item) for item in data.get("results", [])],
        )


@dataclass
class DocumentResponse:
    """Response wrapper for a single document.

    Attributes:
        document: Document payload as returned by the server.
    """

    document: Document


@dataclass
class PdfResponse:
    """Response wrapper for a binary PDF payload.

    Attributes:
        content: Raw PDF bytes.
    """

    content: bytes


@dataclass
class SearchResultObject:
    """Search result payload returned by query endpoint.

    Attributes:
        time: Query execution time reported by the server.
        original_query: Original user query before rewriting.
        query: Effective query executed by SeekStorm.
        offset: Result offset used for paging.
        length: Number of returned results.
        count: Number of matched results returned/visible for this request.
        count_total: Total number of matches across the index.
        query_terms: Tokenized query terms used internally.
        results: List of matched documents.
        facets: Facet aggregation results.
        suggestions: Suggested query alternatives.
    """

    time: int = 0
    original_query: str = ""
    query: str = ""
    offset: int = 0
    length: int = 0
    count: int = 0
    count_total: int = 0
    query_terms: List[str] = field(default_factory=list)
    results: List[Document] = field(default_factory=list)
    facets: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchResultObject":
        return cls(
            time=int(data.get("time", 0)),
            original_query=str(data.get("original_query", "")),
            query=str(data.get("query", "")),
            offset=int(data.get("offset", 0)),
            length=int(data.get("length", 0)),
            count=int(data.get("count", 0)),
            count_total=int(data.get("count_total", 0)),
            query_terms=list(data.get("query_terms", []) or []),
            results=list(data.get("results", []) or []),
            facets=dict(data.get("facets", {}) or {}),
            suggestions=list(data.get("suggestions", []) or []),
        )


def _to_payload_from_dataclass(value: Any) -> Dict[str, Any]:
    if not is_dataclass(value):
        raise TypeError("Expected dataclass instance")
    return _to_payload(asdict(value))


def _to_payload(value: Any) -> Any:
    if is_dataclass(value):
        if hasattr(value, "to_payload"):
            return _to_payload(getattr(value, "to_payload")())
        return _to_payload_from_dataclass(value)
    if isinstance(value, dict):
        return {key: _to_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_payload(item) for item in value]
    if isinstance(value, tuple):
        return [_to_payload(item) for item in value]
    return value


class BaseSeekStormClient:
    """Common base for URL building, headers and response handling."""

    def __init__(self, base_url: str, apikey_base64: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.apikey_base64 = apikey_base64

    def _url(self, path: str, base_url: Optional[str] = None) -> str:
        resolved_base_url = (base_url or self.base_url).rstrip("/")
        return f"{resolved_base_url}{path}"

    def _headers(self, apikey: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        key = apikey if apikey is not None else self.apikey_base64
        if key:
            headers["apikey"] = key
        if extra:
            headers.update(extra)
        return headers

    def _ensure_success(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        raise SeekStormApiError(response.status_code, response.text)

    def _parse_int_body(self, response: httpx.Response) -> int:
        self._ensure_success(response)
        body = response.text.strip()

        # Some server versions return plain numbers, others wrap them as {"Ok": number}.
        try:
            parsed = response.json()
            if isinstance(parsed, int):
                return parsed
            if isinstance(parsed, str):
                return int(parsed)
            if isinstance(parsed, dict):
                for key in ("Ok", "ok", "value", "result"):
                    if key in parsed:
                        return int(parsed[key])
        except Exception:
            pass

        try:
            return int(body)
        except ValueError as exc:
            raise SeekStormApiError(response.status_code, f"Expected integer response, got: {body}") from exc


class SeekStorm(BaseSeekStormClient):
    """Synchronous SeekStorm REST client with typed request/response dataclasses."""

    def __init__(self, base_url: str, apikey_base64: Optional[str] = None, timeout: float = 30.0):
        super().__init__(base_url=base_url, apikey_base64=apikey_base64)
        self.client = httpx.Client(timeout=timeout)

    def live(self, base_url: Optional[str] = None) -> LiveResponse:
        response = self.client.get(self._url("/api/v1/live", base_url=base_url), headers=self._headers())
        self._ensure_success(response)
        return LiveResponse(message=response.text)

    def create_apikey(
        self,
        master_apikey: str,
        api_key_quota_object: ApikeyQuotaObject,
        base_url: Optional[str] = None,
    ) -> ApiKeyResponse:
        response = self.client.post(
            self._url("/api/v1/apikey", base_url=base_url),
            json=_to_payload(api_key_quota_object),
            headers=self._headers(apikey=master_apikey),
        )
        self._ensure_success(response)
        return ApiKeyResponse(api_key_base64=response.text)

    def delete_apikey(
        self,
        apikey_base64: str,
        master_apikey_base64: str,
        base_url: Optional[str] = None,
    ) -> RemainingApiKeysResponse:
        request = DeleteApikeyRequest(apikey_base64=apikey_base64)
        response = self.client.request(
            "DELETE",
            self._url("/api/v1/apikey", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=master_apikey_base64),
        )
        return RemainingApiKeysResponse(remaining_api_keys=self._parse_int_body(response))

    def get_apikey_info(
        self,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> ApikeyInfoResponse:
        response = self.client.get(
            self._url("/api/v1/apikey", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return _parse_apikey_info_payload(response.json())

    def create_index(
        self,
        request: CreateIndexRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> CreateIndexResponse:
        response = self.client.post(
            self._url("/api/v1/index", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        return CreateIndexResponse(index_id=self._parse_int_body(response))

    def delete_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> RemainingIndicesResponse:
        response = self.client.delete(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return RemainingIndicesResponse(remaining_indices=self._parse_int_body(response))

    def clear_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            content=b"clear",
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def commit_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.patch(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def get_index_info(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexResponseObject:
        response = self.client.get(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return IndexResponseObject.from_dict(response.json())

    def index_document(
        self,
        index_id: int,
        document: Document,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.post(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=document,
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def index_documents(
        self,
        index_id: int,
        documents: Sequence[Document],
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.post(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=list(documents),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def index_pdf(
        self,
        index_id: int,
        file_path: Union[str, Path],
        file_date: int,
        document: bytes,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.post(
            self._url(f"/api/v1/index/{index_id}/file", base_url=base_url),
            content=document,
            headers=self._headers(
                apikey=apikey_base64,
                extra={"file": str(file_path), "date": str(file_date)},
            ),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def get_pdf(
        self,
        index_id: int,
        doc_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> PdfResponse:
        response = self.client.get(
            self._url(f"/api/v1/index/{index_id}/file/{doc_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return PdfResponse(content=response.content)

    def get_document(
        self,
        index_id: int,
        doc_id: int,
        request: GetDocumentRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> DocumentResponse:
        response = self.client.request(
            "GET",
            self._url(f"/api/v1/index/{index_id}/doc/{doc_id}", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return DocumentResponse(document=response.json())

    def update_document(
        self,
        index_id: int,
        request: UpdateDocumentRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.patch(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def update_documents(
        self,
        index_id: int,
        request: UpdateDocumentsRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.patch(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def delete_document_by_docid(
        self,
        index_id: int,
        doc_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.delete(
            self._url(f"/api/v1/index/{index_id}/doc/{doc_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def delete_documents_by_docid(
        self,
        index_id: int,
        doc_id_vec: Sequence[int],
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=list(doc_id_vec),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def delete_documents_by_query(
        self,
        index_id: int,
        query: SearchRequestObject,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=query.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    def document_iterator(
        self,
        index_id: int,
        request: GetIteratorRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IteratorResult:
        response = self.client.post(
            self._url(f"/api/v1/index/{index_id}/iterator", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return IteratorResult.from_dict(response.json())

    def query_index(
        self,
        index_id: int,
        request: SearchRequestObject,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> SearchResultObject:
        response = self.client.post(
            self._url(f"/api/v1/index/{index_id}/query", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return SearchResultObject.from_dict(response.json())

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "SeekStorm":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class AsyncSeekStorm(BaseSeekStormClient):
    """Asynchronous SeekStorm REST client with typed request/response dataclasses."""

    def __init__(self, base_url: str, apikey_base64: Optional[str] = None, timeout: float = 30.0):
        super().__init__(base_url=base_url, apikey_base64=apikey_base64)
        self.client = httpx.AsyncClient(timeout=timeout)

    async def live(self, base_url: Optional[str] = None) -> LiveResponse:
        response = await self.client.get(self._url("/api/v1/live", base_url=base_url), headers=self._headers())
        self._ensure_success(response)
        return LiveResponse(message=response.text)

    async def create_apikey(
        self,
        master_apikey: str,
        api_key_quota_object: ApikeyQuotaObject,
        base_url: Optional[str] = None,
    ) -> ApiKeyResponse:
        response = await self.client.post(
            self._url("/api/v1/apikey", base_url=base_url),
            json=_to_payload(api_key_quota_object),
            headers=self._headers(apikey=master_apikey),
        )
        self._ensure_success(response)
        return ApiKeyResponse(api_key_base64=response.text)

    async def delete_apikey(
        self,
        apikey_base64: str,
        master_apikey_base64: str,
        base_url: Optional[str] = None,
    ) -> RemainingApiKeysResponse:
        request = DeleteApikeyRequest(apikey_base64=apikey_base64)
        response = await self.client.request(
            "DELETE",
            self._url("/api/v1/apikey", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=master_apikey_base64),
        )
        return RemainingApiKeysResponse(remaining_api_keys=self._parse_int_body(response))

    async def get_apikey_info(
        self,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> ApikeyInfoResponse:
        response = await self.client.get(
            self._url("/api/v1/apikey", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return _parse_apikey_info_payload(response.json())

    async def create_index(
        self,
        request: CreateIndexRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> CreateIndexResponse:
        response = await self.client.post(
            self._url("/api/v1/index", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        return CreateIndexResponse(index_id=self._parse_int_body(response))

    async def delete_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> RemainingIndicesResponse:
        response = await self.client.delete(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return RemainingIndicesResponse(remaining_indices=self._parse_int_body(response))

    async def clear_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            content=b"clear",
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def commit_index(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.patch(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def get_index_info(
        self,
        index_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexResponseObject:
        response = await self.client.get(
            self._url(f"/api/v1/index/{index_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return IndexResponseObject.from_dict(response.json())

    async def index_document(
        self,
        index_id: int,
        document: Document,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.post(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=document,
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def index_documents(
        self,
        index_id: int,
        documents: Sequence[Document],
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.post(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=list(documents),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def index_pdf(
        self,
        index_id: int,
        file_path: Union[str, Path],
        file_date: int,
        document: bytes,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.post(
            self._url(f"/api/v1/index/{index_id}/file", base_url=base_url),
            content=document,
            headers=self._headers(
                apikey=apikey_base64,
                extra={"file": str(file_path), "date": str(file_date)},
            ),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def get_pdf(
        self,
        index_id: int,
        doc_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> PdfResponse:
        response = await self.client.get(
            self._url(f"/api/v1/index/{index_id}/file/{doc_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return PdfResponse(content=response.content)

    async def get_document(
        self,
        index_id: int,
        doc_id: int,
        request: GetDocumentRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> DocumentResponse:
        response = await self.client.request(
            "GET",
            self._url(f"/api/v1/index/{index_id}/doc/{doc_id}", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return DocumentResponse(document=response.json())

    async def update_document(
        self,
        index_id: int,
        request: UpdateDocumentRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.patch(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def update_documents(
        self,
        index_id: int,
        request: UpdateDocumentsRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.patch(
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def delete_document_by_docid(
        self,
        index_id: int,
        doc_id: int,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.delete(
            self._url(f"/api/v1/index/{index_id}/doc/{doc_id}", base_url=base_url),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def delete_documents_by_docid(
        self,
        index_id: int,
        doc_id_vec: Sequence[int],
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=list(doc_id_vec),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def delete_documents_by_query(
        self,
        index_id: int,
        query: SearchRequestObject,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IndexedDocumentCountResponse:
        response = await self.client.request(
            "DELETE",
            self._url(f"/api/v1/index/{index_id}/doc", base_url=base_url),
            json=query.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        return IndexedDocumentCountResponse(indexed_document_count=self._parse_int_body(response))

    async def document_iterator(
        self,
        index_id: int,
        request: GetIteratorRequest,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> IteratorResult:
        response = await self.client.post(
            self._url(f"/api/v1/index/{index_id}/iterator", base_url=base_url),
            json=_to_payload(request),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return IteratorResult.from_dict(response.json())

    async def query_index(
        self,
        index_id: int,
        request: SearchRequestObject,
        apikey_base64: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> SearchResultObject:
        response = await self.client.post(
            self._url(f"/api/v1/index/{index_id}/query", base_url=base_url),
            json=request.to_payload(),
            headers=self._headers(apikey=apikey_base64),
        )
        self._ensure_success(response)
        return SearchResultObject.from_dict(response.json())

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncSeekStorm":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
