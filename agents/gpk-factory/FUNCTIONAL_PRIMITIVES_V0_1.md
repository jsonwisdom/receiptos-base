# GPK Factory Functional Primitives v0.1

**Factory:** Jay's GitHub Garbage Pail Kids Factory  
**Mode:** TEXT_ONLY  
**Authority:** false  
**Media Output:** forbidden  
**Image Prompt Output:** forbidden  
**Delivery Methods:** forbidden

## Purpose

This document defines protocol-level functional primitives for the GPK Factory.

These primitives are not media outputs.  
These primitives are not image prompts.  
These primitives are not delivery methods.

They are callable text-only behaviors that let the factory remain entertaining while preserving the governance membrane.

## Core Rule

```text
FUNCTIONAL_SLOT_ALLOWED
MEDIA_OUTPUT_FORBIDDEN
IMAGE_PROMPT_FORBIDDEN
DELIVERY_METHOD_FORBIDDEN
AUTHORITY_FALSE
```

## Constraint Primitives

### 1. `no_image()`

Asserts that the current operation must not produce, request, reference, or attach an image artifact.

```js
function no_image() {
  return {
    type: "constraint",
    id: "NO_IMAGE",
    description: "This operation must not generate, request, reference, or attach any image artifact."
  };
}
```

### 2. `no_image_prompt()`

Prevents the system from generating or consuming prompts intended for image creation.

```js
function no_image_prompt() {
  return {
    type: "constraint",
    id: "NO_IMAGE_PROMPT",
    description: "This operation must not generate or consume any prompt intended for image creation."
  };
}
```

### 3. `no_delivery_methods()`

Prevents transport semantics such as upload, download, send, deliver, transmit, publish, mint, or distribute.

```js
function no_delivery_methods() {
  return {
    type: "constraint",
    id: "NO_DELIVERY_METHODS",
    description: "This operation must not invoke, simulate, or describe delivery, transport, publication, or transmission methods."
  };
}
```

## Composite Constraint Envelope

### 4. `apply_text_only_constraints()`

Binds the hard constraints into one reusable membrane envelope.

```js
function apply_text_only_constraints() {
  return {
    constraints: [
      no_image(),
      no_image_prompt(),
      no_delivery_methods()
    ],
    mode: "TEXT_ONLY",
    authority: false,
    description: "All operations must remain purely textual, protocol-driven, and non-delivery."
  };
}
```

## Entertainment-Safe Functional Primitives

### 5. `render_character_card_text(character_id, attributes)`

Creates a text-only character card representation.

```js
function render_character_card_text(character_id, attributes) {
  return {
    type: "character_card_text",
    id: character_id,
    attributes,
    constraints: apply_text_only_constraints(),
    authority: false
  };
}
```

### 6. `simulate_factory_run(run_id, parameters)`

Runs a playful factory simulation entirely as structured text.

```js
function simulate_factory_run(run_id, parameters) {
  return {
    type: "factory_simulation_text",
    id: run_id,
    parameters,
    constraints: apply_text_only_constraints(),
    authority: false
  };
}
```

### 7. `generate_story_event(event_id, context)`

Creates a text-only narrative event for entertainment and continuity testing.

```js
function generate_story_event(event_id, context) {
  return {
    type: "story_event_text",
    id: event_id,
    context,
    constraints: apply_text_only_constraints(),
    authority: false
  };
}
```

## Factory Interpretation

The primitives above represent functional slots. They do not execute media actions.

Allowed:

```text
text card metadata
text character description
text factory simulation
text story event
text receipt packet
text continuity report
```

Forbidden:

```text
image artifact
image prompt
media delivery
publication action
minting action
transport action
```

## Governance Boundary

Every primitive must preserve:

```text
authority: false
canon_mutation: false unless explicitly passed through canon freeze workflow
real_canon_touched: false during disposable test lane
no_image: true
no_image_prompt: true
no_delivery_methods: true
```

## Status

```text
FUNCTIONAL_PRIMITIVES_DEFINED: true
TEXT_ONLY_MEMBRANE: locked
MEDIA_GENERATION: forbidden
DELIVERY_METHODS: forbidden
AUTHORITY: false
```
