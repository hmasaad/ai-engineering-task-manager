# Research: Workflow Observability and Distributed Tracing

## Decision: One trace per task, one span per running step

**Rationale**: The workflow already runs one step at a time on one task. That run is the trace. The first step that starts opens it. Later steps add spans to the same trace. The first span follows nothing. Every later span follows that first span, so the path can be read from the start of the run. A second task has its own trace.

**Alternatives considered**: A new trace for every advance. Rejected because the engineer would lose the path from the first step to the later ones. One span for the whole workflow. Rejected because a failed step would hide which step ran.

## Decision: Open the span with the start, and close it with the outcome

**Rationale**: A step is stored as Running before the result is stored. The span opens in that same result, with no end time. The result that marks the step Completed, Failed, or Waiting closes that span with the same state, detail, and time. A start that is rolled back leaves no trace. Opening the task does not invent spans for steps that already finished.

**Alternatives considered**: Building the trace only when the engineer asks for it. Rejected because a running step would have no stored start until someone looked. Closing the span in a later request. Rejected because a crash between the outcome and the span would show a step that finished and a span that is still running.

## Decision: Reading the trace writes nothing

**Rationale**: The trace is a record. The read returns the stored spans, does not call the clock, and does not start a step. A second read returns the same spans. Delivery, rejection, and compensation stay without spans so this change can be checked on its own.
