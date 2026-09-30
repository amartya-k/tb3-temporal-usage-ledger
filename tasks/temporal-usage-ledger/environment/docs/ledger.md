# Durable billing contract

This contract and `billing.md` are normative. All data are synthetic. The service is used by a billing backend receiving at-least-once CDC events from independent producer partitions. Producer order and billing `recorded` time are separate dimensions.

## Invocation and durability

`python /app/app/ledger.py DATABASE REQUEST_JSON RESPONSE_JSON` handles one JSON request. Write one JSON response to the supplied file and exit zero for successful operations and the domain errors below. Unexpected operational failures may exit nonzero. All successful mutations, their idempotency receipts, and resulting outbox changes must commit atomically. Separate processes may invoke the same database concurrently. Their outcomes must be equivalent to a serial ordering that respects completed calls. Readers see a single consistent committed state. Retrying after a killed writer must yield either the original completed response or the effect of one fresh execution, never a partial mutation or duplicate charge.

A missing/empty database starts empty. Existing version-1 SQLite databases have `PRAGMA user_version=1` and the following tables:

```sql
CREATE TABLE history (source TEXT, seq INTEGER, kind TEXT, payload TEXT,
                      PRIMARY KEY (source, seq));
CREATE TABLE offsets (source TEXT PRIMARY KEY, committed INTEGER NOT NULL);
```

`kind` is `sessions` or `tariffs`; `payload` is a JSON object using the billing schema. Each partition in `offsets` contains every history row 1 through `committed` with no gaps; history may also contain rows above that offset, which are buffered and not yet visible. Those rows and offsets must survive migration. Migration is transparent, idempotent and safe under concurrent first use and interruption. There are no preexisting invoices, outbox entries or receipts. No internal schema is prescribed after migration.

Well-formed inputs satisfy the schemas below, except intentional domain conflicts. Strings can include quotes, non-ASCII characters and newlines. Integers and booleans retain JSON types. The batch API limits in `billing.md` apply to that API only. For the ledger there are at most 2,000 events, 100 invoices, 50 sources, and 12 concurrent invocations. An invocation completes within 30 seconds on 2 CPUs and 2 GB RAM once competing operations release the database. Billing ranges may span 2,000,000,000 seconds. This is a correctness task, not a throughput benchmark.

## Mutations and receipts

`ingest`, `settle` and `ack` require a nonempty string `request_id`. Request IDs share one namespace across all mutation types. An identical replay returns the **original response**, even if the database has changed since. Identity compares the complete request as a JSON value: object key order is irrelevant, array order matters. Reusing a successful request ID with a different request returns `{"error":"request_conflict"}`. A failed operation leaves no receipt and no changes; its request ID is reusable. Check receipts before other domain validation. Reads have no request ID.

All errors are exactly `{"error":CODE}`. For otherwise well-formed requests that contain more than one conflict, any applicable error is acceptable, except that `request_conflict` takes precedence.

## Ingest

Request: `{"op":"ingest","request_id":STRING,"events":[EVENT,...]}`.
EVENT is `{"source":STRING,"seq":POSITIVE_INTEGER,"kind":"sessions"|"tariffs","payload":REVISION}`. Sequences start at 1 independently for each source. `payload` uses the full session/tariff revision schema in `billing.md`. An empty batch is valid.

Persist every event, including events received ahead of a gap. A source watermark is its greatest contiguous received sequence starting from 1. Only rows at or below the watermark are eligible for billing. Close gaps transitively, including previously buffered events. The response is `{"watermarks":{SOURCE:INTEGER,...}}` for all known sources, including watermark zero. No rows may be lost when the process exits.

Replaying an identical `(source,seq)` event is a no-op. A different kind or payload at that position returns `event_conflict`. Across **all** received rows, including buffered rows, `(kind,payload.id,payload.recorded,payload.revision)` identifies one immutable logical revision. A different payload with this identity returns `revision_conflict`; an identical revision delivered on several sources or sequences is legal and must not be double counted. Validation and all event/watermark changes for the entire batch are atomic, including conflicts within the batch.

## Historical reads

Request: `{"op":"query","frontier":VECTOR_OR_NULL,"queries":[QUERY,...]}`. QUERY has the billing query schema. Null frontier means the current complete watermark vector. An explicit vector assigns nonnegative sequence cutoffs to named sources; omitted known sources have cutoff zero. An unknown source at cutoff zero is allowed; an unknown positive cutoff or any cutoff above the source watermark returns `frontier_unavailable`.

A snapshot sees an event only if its sequence is at or below **both** its source watermark and the requested cutoff. From those rows, collapse duplicate logical revisions and apply the separate `as_of` revision selection from `billing.md`. A later delivered correction must not alter an earlier frontier snapshot, even if its `recorded` time is earlier. The query response is exactly the batch `{"queries":[...]}` response. Reads never advance watermarks or create receipts.

## Settlement and corrections

Request: `{"op":"settle","request_id":STRING,"invoice_id":STRING,"expected_version":NONNEGATIVE_INTEGER,"frontier":VECTOR_OR_NULL,"query":QUERY}`.

An absent invoice has current version zero; otherwise compare against its last committed version. A mismatch returns `version_conflict`. For an existing invoice, query `id`, `start` and `end` must match its original query or return `invoice_conflict`; `as_of` may change. Compute a new invoice using one snapshot, then commit version `expected_version+1` and an outbox entry together. Even identical totals create a new version. Frozen invoice history must never be recomputed using later data.

Return DOCUMENT:

```json
{"invoice_id":"example","version":1,"frontier":{"source":2},
 "query":{"id":"q","as_of":20,"start":0,"end":10},
 "accounts":[{"account":"A","units":5,"unpriced_units":0,"charge_cents":2}],
 "delta":[{"account":"A","units":5,"unpriced_units":0,"charge_cents":2}],
 "outbox_seq":1}
```

Types are those in the example and billing contract. `frontier` is the resolved snapshot, normalized to contain only positive cutoffs (including for a null request frontier). `accounts` is the new complete invoice. `delta` subtracts the **previous version's rounded account totals** from the new ones, across the union of accounts. Missing accounts are zeros; include an account in `delta` iff any of its three differences is nonzero. Sort `accounts` and `delta` by account. Delta values may be negative. Version one subtracts an empty invoice. Rounding a raw millicent difference is incorrect. `outbox_seq` is a gap-free global integer starting at 1 across all invoices; rejected/replayed requests allocate nothing.

Read: `{"op":"invoice","invoice_id":STRING,"version":POSITIVE_INTEGER_OR_NULL}` returns the frozen DOCUMENT, with null meaning latest. A missing invoice/version returns `not_found`.

## Outbox

Request: `{"op":"outbox","after":NONNEGATIVE_INTEGER,"limit":POSITIVE_INTEGER}` returns `{"entries":[DOCUMENT,...]}` for unacknowledged documents with `outbox_seq > after`, sorted by sequence, limited to `limit`.

Request: `{"op":"ack","request_id":STRING,"sequences":[POSITIVE_INTEGER,...]}` atomically marks those exact outbox entries acknowledged and returns `{"acked":[...sorted distinct input sequences...]}`. Already acknowledged entries are allowed. A nonexistent sequence returns `outbox_missing` and changes nothing. Acknowledgment neither deletes invoice history nor renumbers subsequent entries. An empty list is valid.
