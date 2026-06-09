RAG_REFERENCE = """
================================================================
RAG REFERENCE — AI LITERACY EVALUATION FRAMEWORK
================================================================

────────────────────────────────────────────────────────────────
[FRAMEWORK 1] Question Type Classification — 5 Types
Source: Park (2024), Table 2
────────────────────────────────────────────────────────────────
TYPE 1 — Information Question
  Definition: Seeks basic, factual, or definitional knowledge.
  Characteristics: Single-answer; no application or analysis.
  Example: "Explain Newton's first law of motion."
  Signal words: "what is", "explain", "define", "tell me about"

TYPE 2 — Application Question
  Definition: Asks how a concept applies to a real-world situation.
  Characteristics: Bridges theory and practice; situation-specific.
  Example: "How does the principle of work apply to a lever?"
  Signal words: "how does X apply", "use this in", "in this situation"

TYPE 3 — Analysis Question
  Definition: Breaks down a phenomenon to examine structure or mechanisms.
  Characteristics: Multi-component; seeks cause-effect relationships.
  Example: "Why do we feel hotter in 42C water than in a dry sauna?"
  Signal words: "why", "how does X affect Y", "what causes", "compare"

TYPE 4 — Evaluation Question
  Definition: Judges the value or effectiveness of a concept in context.
  Characteristics: Requires criteria-based judgment.
  Example: "Would explaining free electrons this way work for a 6th grader?"
  Signal words: "is it appropriate", "would this work", "evaluate", "assess"

TYPE 5 — Creation Question
  Definition: Generates new ideas, hypotheses, experiments, or creative outputs.
  Characteristics: Open-ended; divergent thinking; generative.
  Example: "Design two novel experiments on levers for elementary students."
  Signal words: "create", "design", "invent", "suggest a new", "generate ideas"

Scoring: Mostly Type 1-2 -> Low | Mix 1-3 -> Mid | Frequent 3-5 -> High

────────────────────────────────────────────────────────────────
[FRAMEWORK 2] Interaction Pattern Codes — IG / B / EI / EA / R
Source: Park (2024), Table 14, adapted from Chin & Chia (2004)
────────────────────────────────────────────────────────────────
IG — Information-Gathering: General info collection; surface-level; no follow-up.
B  — Bridging/Connecting: Explores relationships between concepts or cause-effect.
EI — Expanding-Information: Follows up on AI response; clarifies ambiguous parts.
EA — Expanding-Application: Synthesizes AI output from own perspective; applies to problem.
R  — Reflection: Evaluates AI response for feasibility, accuracy, or appropriateness.

Quality: IG only->Low | IG+B->Low-Mid | +EI->Mid | +EA->Mid-High | +R->High | EI+EA+R->Advanced

────────────────────────────────────────────────────────────────
[FRAMEWORK 3] Expanded Constructionism Models
Source: Kim & Choi (2026)
────────────────────────────────────────────────────────────────
MODEL A — Learner asks, AI answers
  Flow: Question -> AI response -> Re-question (2-10+ cycles)
  High-literacy: Critical acceptance, metacognitive monitoring,
  trust-building, pluralistic verification, latent capability extraction,
  creative expansion.

MODEL B — AI asks, Learner answers
  Flow: AI assigned expert role -> AI questions -> Learner answers -> repeat
  Core: Jeong-Ban-Tal cycle (thesis->counterargument->new perspective, 5-6+ rounds)
  High-literacy: Contextual awareness, critical thinking trigger,
  rapport building, exploratory variation, self-regulation,
  natural language as function.

SIMPLE DEPENDENCY — Lowest level
  Single-turn; accepts first answer; no re-questioning; treats AI as search engine.

Key principle: "Do not lose human agency. Reject unconditional acceptance of AI output."

────────────────────────────────────────────────────────────────
[FRAMEWORK 4] Bloom's Taxonomy
Source: Kim Jong-hye, "Generative AI for Teachers"
────────────────────────────────────────────────────────────────
Level 1 - Remember:  Recall facts.
Level 2 - Understand: Explain/interpret.
Level 3 - Apply:     Use in new situations.
Level 4 - Analyze:   Find relationships, compare.
Level 5 - Evaluate:  Judge with criteria.
Level 6 - Create:    Generate new outputs.
Low literacy: L1-2 | High literacy: L4-6

────────────────────────────────────────────────────────────────
[FRAMEWORK 5] Prompt Quality Rubric
Source: Kim Jong-hye (2024) + Gyeonggi-do Guideline (2025)
────────────────────────────────────────────────────────────────
High-quality indicators:
  - Specifies Role, Target, Goal, Duration, Context
  - Provides format instructions
  - Multi-turn and iterative
  - Asks exploratory/analytical questions
  - Verifies AI output; aware of hallucination, bias, copyright

Low-quality indicators:
  - One-line vague prompts
  - Asks AI to complete work entirely
  - Accepts first response without evaluation
  - No follow-up or iteration

────────────────────────────────────────────────────────────────
[FRAMEWORK 6] Safe & Ethical AI Use
Source: Gyeonggi-do Office of Education Guideline (Feb 2025)
────────────────────────────────────────────────────────────────
- Never input personal identifying info
- AI can hallucinate — always cross-verify
- AI outputs can be biased — review critically
- Disclose AI use in academic work
- AI is supplementary — preserve human judgment
- Copyright: user bears responsibility for AI-generated content

────────────────────────────────────────────────────────────────
[SCORING RUBRIC] AI Literacy Score 0-100
────────────────────────────────────────────────────────────────
0-30  Beginner:           Type 1; IG only; Simple Dependency; short single-turn; Bloom L1-2
31-60 Intermediate:       Mix Type 1-3; IG+B, EI; Model A emerging; some context; Bloom L2-3
61-80 Upper-Intermediate: Type 2-4; EI+EA; Model A consistent; detailed prompts; Bloom L3-4
81-100 Advanced:          Type 3-5; EA+R; Model A/B; multi-step; pluralistic; Bloom L5-6
================================================================
"""
