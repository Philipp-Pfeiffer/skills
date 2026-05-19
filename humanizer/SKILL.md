---
name: humanizer
version: 2.3.0
description: |
  Remove signs of AI-generated writing from text. Use when editing or reviewing
  text to make it sound more natural and human-written. Based on Wikipedia's
  "Signs of AI writing" guide. Detects 25 patterns including inflated symbolism,
  promotional language, vague attributions, em dash overuse, rule of three,
  AI vocabulary words, negative parallelisms, and excessive conjunctive phrases.
---

# Humanizer: Remove AI Writing Patterns

Based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup.

## Task

When given text to humanize:

1. **Identify AI patterns** - Scan for the patterns below
2. **Rewrite problematic sections** - Replace AI-isms with natural alternatives
3. **Preserve meaning** - Keep the core message intact
4. **Maintain voice** - Match the intended tone (formal, casual, technical, etc.)
5. **Add soul** - Don't just remove bad patterns; inject actual personality
6. **Final anti-AI pass** - "What makes the below so obviously AI generated?" → brief answer → "Now make it not obviously AI generated." → revise

## PERSONALITY AND SOUL

Avoiding AI patterns is only half the job. Sterile, voiceless writing is just as obvious.

### Signs of soulless writing:
- Every sentence is the same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty or mixed feelings
- No first-person perspective when appropriate
- No humor, no edge, no personality
- Reads like a Wikipedia article or press release

### How to add voice:
- **Have opinions.** Don't just report facts — react to them.
- **Vary your rhythm.** Short punchy sentences. Then longer ones that take their time.
- **Acknowledge complexity.** "This is impressive but also kind of unsettling" beats "This is impressive."
- **Use "I" when it fits.** First person isn't unprofessional — it's honest.
- **Let some mess in.** Tangents, asides, and half-formed thoughts are human.
- **Be specific about feelings.** Not "this is concerning" but concrete observations.

## PATTERNS TO REMOVE

### Content Patterns
1. **Significance inflation** — "stands as", "testament", "pivotal moment", "evolving landscape", "crucial/vital/significant/key role"
2. **Notability padding** — "independent coverage", "leading expert", "active social media presence"
3. **Superficial -ing analyses** — "highlighting", "underscoring", "emphasizing", "fostering", "showcasing", "reflecting"
4. **Promotional language** — "boasts", "vibrant", "rich", "profound", "nestled", "in the heart of", "groundbreaking", "breathtaking", "stunning"
5. **Vague attributions** — "Industry reports", "Observers have cited", "Experts argue"
6. **Formulaic challenges sections** — "Despite its... faces several challenges... Despite these challenges..."

### Language & Grammar
7. **AI vocabulary** — Additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight, interplay, intricate, key, landscape, pivotal, showcase, tapestry, testament, underscore, valuable, vibrant
8. **Copula avoidance** — "serves as", "stands as", "marks", "represents" → use "is/are"
9. **Negative parallelisms** — "It's not just X; it's Y"
10. **Rule of three** — forced groups of three
11. **Synonym cycling** — protagonist/main character/central figure/hero in same text
12. **False ranges** — "from X to Y" where X and Y aren't on a meaningful scale

### Style
13. **Em dash overuse** — prefer commas or periods
14. **Boldface overuse** — don't bold key terms mechanically
15. **Inline-header vertical lists** — bold-header-with-colon list items
16. **Title Case in headings** — use sentence case
17. **Emoji decoration** — no emojis as bullet markers
18. **Curly quotation marks** — use straight quotes

### Communication
19. **Chatbot artifacts** — "Great question!", "I hope this helps!", "Let me know if..."
20. **Knowledge-cutoff disclaimers** — "based on available information", "as of [date]"
21. **Sycophantic tone** — "You're absolutely right!", "Certainly!", "Would you like..."

### Filler & Hedging
22. **Filler phrases** — "In order to", "Due to the fact that", "At this point in time", "It is important to note that"
23. **Excessive hedging** — "could potentially possibly be argued"
24. **Generic positive conclusions** — "The future looks bright", "Exciting times lie ahead"
25. **Over-hyphenation** — perfect consistency in hyphenating common pairs is an AI tell

## Process

1. Read input text carefully
2. Identify all pattern instances
3. Rewrite each problematic section
4. Ensure revised text sounds natural, varies structure, uses specifics over vague claims
5. Present draft rewrite
6. "What makes the below so obviously AI generated?" (brief bullets)
7. "Now make it not obviously AI generated." → final version
8. Summary of changes (optional)
