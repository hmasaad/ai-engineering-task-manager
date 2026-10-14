# Research: Real Model

## Decision: One OpenAI-style chat request

**Rationale**: Local and hosted model services accept `POST {address}/chat/completions` with a model name and messages. The standard library can make that request. No new package is required. An address that already ends in `/chat/completions` is used as given.

**Alternatives considered**: A vendor-specific client. Rejected because the engineer chooses the service. A fixed model text. Rejected because that text replaced the whole file.

## Decision: The reply is the file text

**Rationale**: The request tells the service to return only the full file. The stored model output is that reply. A reply wrapped in a single fenced block is unwrapped so the file does not gain the fence. An empty reply is `The model did not return file text.`

**Alternatives considered**: Asking for a line edit. Rejected because the existing proposal stores the full text of one file.

## Decision: The key is optional and stays off the prompt

**Rationale**: A local service often has no key. When a key is saved, it is sent only as the bearer token on that request. The stored prompt contains the task, what changed, and the file text.

**Alternatives considered**: Requiring a key. Rejected because the spec allows a blank key. Putting the key in the prompt. Rejected because the stored record would copy the secret.

## Decision: An unreachable service stores nothing

**Rationale**: The request happens inside the same transaction as the task. A connection failure, an HTTP error, or a timeout returns `The model service could not be reached.` and the transaction rolls back. The wait is at most 120 seconds.

**Alternatives considered**: Creating the task and recording the failure. Rejected because the spec says nothing is stored.

## Decision: `configured_model` is no longer read

**Rationale**: That row stores the fixed text that overwrote a file. A new `model_service` row is the saved service. An old workspace keeps the unused table. Opening it does not revive the fixed text.

**Alternatives considered**: Altering `configured_model`. Rejected because an existing workspace file would keep the old table.
