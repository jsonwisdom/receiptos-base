# Event-Time Semantics Boundary

Issue: #42

## Purpose

This document opens the event-time lane as a boundary only.

No parser, extractor, sorter, consumer, or runtime code is introduced here.

## Closed storage-time stack

The storage-time stack is closed and out of scope for event-time work.

Closed references:

- #40 Storage-Time Sorted View
- #41 Storage-View Subscription Feed v0

Event-time work must not modify #40 or #41 artifacts.

## Definitions

Storage-time means the time a record was stored or logged.

Event-time means a time claimed by an external source about the world.

Storage-time order and event-time order are separate.

## Firewall rules

Event-time semantics must not inherit authority from storage-time ordering.

Event-time semantics must not treat storage-time order as event order.

Event-time semantics must not infer causation from storage-time order.

Event-time semantics must not infer priority from storage-time order.

Event-time semantics must not infer evidentiary strength from storage-time order.

## First implementation rule

Before any event-time parser, extractor, sorter, or consumer is added, a separate conformance gate must exist.

That gate must fail if event-time code imports storage-time view modules directly.

## Required future separation

Future event-time work must use a separate path, such as:

```text
semantics/event_time/
```

or:

```text
event_time/
```

The storage-time audit path remains closed infrastructure.

## Sticky fields

Event-time work must preserve:

```text
authority=false
truth_claim=false
inference_performed=false
state_mutated=false
```

## Boundary statement

Storage-time proves storage order only.

Event-time may only represent an externally claimed time, subject to its own source and conformance rules.

No event-time claim receives authority from storage-time infrastructure.
