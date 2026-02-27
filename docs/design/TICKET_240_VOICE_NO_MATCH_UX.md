# TICKET_240: Improve Voice Input No-Match Experience

## Status: Open
## Priority: Medium
## Category: Conference / UX
## Parent: TICKET_239
## Date: 2026-02-27

---

## Problem

When a visitor uses voice input and says something that does not match any of the 182 Q&A pairs (e.g. "Hello", "Hi there", "Thank you"), the chatbot displays:

```
No match found for "Hello.".
Try browsing topics above or use different keywords.
Or contact contact@silverstream.tech
```

This is a poor experience for voice users. The fallback message was designed for typed keyword searches, not conversational voice input. Visitors naturally start with greetings or casual speech before asking technical questions.

---

## Scope

Handle the gap between conversational voice input and keyword-based Q&A search. Categories of unmatched voice input:

| Input Type | Example | Current Behavior | Expected Behavior |
|------------|---------|-----------------|-------------------|
| Greeting | "Hello", "Hi" | No match error | Friendly welcome + topic suggestions |
| Gratitude | "Thank you", "Thanks" | No match error | Acknowledgment + invite to ask more |
| Farewell | "Bye", "Goodbye" | No match error | Friendly farewell message |
| Vague/short | "Tell me more", "What?" | No match error | Show category list with prompt to pick a topic |
| Off-topic | "What's the weather" | No match error | LLM fallback (if configured), else voice-aware no-match with topic buttons |
| Technical but no match | "How do you handle TCP" | No match / low score | Voice-aware no-match with topic buttons + LLM fallback (if configured) |
| Noise/misrecognition | Random syllables, < 2 chars | No match error | Silently ignore (no UI update) |

---

## Decision: Approach C (Hybrid)

Client-side intent detection for conversational phrases + voice-aware fallback message for genuine misses + existing LLM fallback when API key is available.

### Why Hybrid

- Intent detection handles ~80% of the problem (greetings, thanks, noise) with zero latency
- Voice-aware fallback improves UX for the remaining genuine misses
- LLM path already exists, no changes needed
- Zero dependencies, deterministic, zero cost
- Standard practice in conversational UX (Dialogflow, Rasa, Botpress all use intent classification before search)

### Anti-Patterns to Avoid

- Do NOT add greeting Q&As to the 182 data set (pollutes technical knowledge base)
- Do NOT use fuzzy matching / Levenshtein for intent detection (overkill)
- Do NOT send greetings to the LLM (wastes API calls, slow, non-deterministic for trivial input)
- Do NOT suppress all no-match messages (genuine technical misses need helpful fallback)

---

## Design

### Architecture: Interception Point

Intent detection runs **before** the search function. The flow becomes:

```
voice input -> intent check -> conversational? -> friendly response (no search)
                            -> question?        -> search -> results / LLM fallback / voice-aware no-match
```

This means `renderLowScoreResults` and `renderFallbackMsg` only handle genuine technical queries with no match.

### 1. Intent Pattern Map

A simple object map in `app.js`. Pattern matching via `String.includes()` or regex on lowercased input. No NLP, no dependencies.

```
INTENTS = {
    greeting:  ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
    gratitude: ["thank you", "thanks", "appreciate", "cheers"],
    farewell:  ["bye", "goodbye", "see you", "take care"],
    vague:     ["tell me more", "what", "huh", "explain", "help"]
}
```

Detection logic: normalize input (lowercase, trim), check if input matches or starts with any pattern. Short-circuit before search.

### 2. Friendly Intent Responses

Each intent maps to a response with actionable next steps:

| Intent | Response | Action |
|--------|----------|--------|
| `greeting` | "Hi! I'm the NexusFIX Q&A assistant. Here are some topics you can ask about:" | Show 3-4 popular category buttons |
| `gratitude` | "You're welcome! Feel free to ask more questions about NexusFIX." | No action needed |
| `farewell` | "Goodbye! Visit the poster for more details, or reach out at contact@silverstream.tech." | No action needed |
| `vague` | "I can answer questions about NexusFIX. Pick a topic to get started:" | Show full category button list |

Responses rendered as a `status-msg` div (existing CSS class), not as error-style messages.

### 3. Voice-Aware No-Match Fallback

Replace `renderFallbackMsg` behavior for voice input:

**Current** (typed-search oriented):
```
No match found for "How do you handle TCP".
Try browsing topics above or use different keywords.
Or contact contact@silverstream.tech
```

**New** (voice-aware):
```
I didn't find a matching Q&A for that.
Here are some topics you can ask about:
[SIMD Parsing] [Memory Management] [FIX Protocol] [Build System] ...
```

Key differences:
- Do NOT echo the query verbatim (voice transcriptions are messy; quoting garbled speech is bad UX)
- Show clickable category buttons instead of "try different keywords"
- Conversational tone, not error tone

### 4. Noise Filtering

Input shorter than 2 characters or containing only non-alphabetic characters: silently ignore. No UI update, no error message. This prevents misrecognized syllables from cluttering the display.

---

## Files Changed

| File | Change | Estimated LOC |
|------|--------|---------------|
| `app.js` | Add intent pattern map, `detectIntent()` function, friendly response renderer, voice-aware fallback | ~60 |

No new files. No changes to `llm.js`, `voice.js`, `tts.js`, `qa-data.js`.

---

## Acceptance Criteria

- [ ] Voice input of "Hello" shows friendly welcome + topic suggestions (not error message)
- [ ] Voice input of "Thank you" shows acknowledgment (not error message)
- [ ] Voice input of "Bye" shows farewell message (not error message)
- [ ] Voice input of "Tell me more" shows category list (not error message)
- [ ] Noise input (< 2 chars, non-alpha) is silently ignored
- [ ] Genuine technical miss shows voice-aware fallback with category buttons (no verbatim query echo)
- [ ] LLM fallback still triggers for off-topic/technical misses when API key is configured
- [ ] Text search behavior unchanged (typed input still uses existing search flow)
- [ ] Visitor is guided toward valid questions / categories in all fallback paths
- [ ] No new dependencies
- [ ] All changes contained within `app.js`

---

## Dependencies

| Ticket | Dependency Type | Why |
|--------|----------------|-----|
| TICKET_239 | Parent | Booth voice mode implementation |
| TICKET_226 | Root | Main chatbot design spec |
