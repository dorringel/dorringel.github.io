---
layout: post
title: "context engineering"
description: "The mechanics of what actually happens when you press Enter."
redirect_from:
  - /context-engineering/
---

Every 12-year-old has ChatGPT in their hand. Millions of developers use LLMs daily. And yet most of them — including many senior engineers — don't understand the fundamental mechanics of how these systems work. Not the linear algebra. The constraints. The ones that determine whether you get a useful answer or garbage.

This post is about those constraints, and why understanding them is the single most valuable skill in AI right now.

## they don't know who you are

Chat models are stateless. Every time you send a message, the model has no memory of previous conversations, no record of who you are, no preferences, no history. Nothing — unless it happened to appear in the training data.

That conversational memory you experience in ChatGPT? That's the application injecting your previous messages back into the context before each call. The personality? A system prompt. The "memory" feature? A database that the application queries and prepends to your conversation. The SOUL.md, USER.md, and CLAUDE.md files that power AI coding assistants? Text files read from disk and stuffed into the prompt.

The model sees none of this as "memory." It sees tokens. Every single time, from scratch.

## probabilistic pattern matching

LLMs are probabilistic machines that produce the next most likely token given everything they saw in training. That's the entire mechanism. The closer your input aligns with patterns the model was trained on, the better the output.

This sounds simple but it has a profound implication: context engineering — the art of shaping what the model sees — is really the art of making your input look like the kind of input the model was trained to complete well. A well-structured prompt that resembles a research paper will get research-paper-quality output. A sloppy prompt will get sloppy completion. You're not "instructing" the model. You're biasing its probability distribution.

This is also why LLMs famously can't count the r's in "strawberry." They don't see characters. They see tokens. "Strawberry" gets split into subword chunks like ["straw", "berry"]. The model never saw individual letters. It's not stupid; it's operating on a completely different unit of reality than you assume.

## finite context, infinite ambition

LLMs have a finite context window. There's been massive progress — from 2,048 tokens in GPT-3 (2020) to 1M+ tokens standard today — but it's still finite. Every conversation turn, every memory, every tool definition, every system instruction competes for space. Context engineering is, in large part, the discipline of deciding what gets in and what doesn't.

And there's a fundamental asymmetry in how that window gets used. Input processing is massively parallel — the model sees all input tokens at once and computes attention in one pass. But generation is autoregressive: to produce token N+1, the model must first generate token N. Each output token is a sequential step. This is why a model can "read" 100K tokens in sub-second latency but generating 1K tokens takes noticeably longer.

## the thinking illusion

LLMs don't have an internal thinking system. They can't do what you do — listen to a friend going through a tough time for ten minutes, pause, reflect, and then say "first, how are you doing? do you need a hug?" Their only way to "think" is to produce tokens. The only thinking scratchpad is the context itself.

**And this includes the "reasoning" and "thinking" models you're using right now.**

OpenAI's o-series, DeepSeek R1, Claude Extended Thinking — they all "think" the exact same way: by generating tokens. The difference is that they produce a hidden stream of "thinking tokens" before the final answer. Those tokens are billed, consume compute, and live in the context like any other token.

How did they learn to reason? Not through an architectural breakthrough — through reinforcement learning. DeepSeek R1-Zero was trained with pure RL: given a problem, generate a chain-of-thought trajectory, get rewarded only if the final answer is correct. Over millions of iterations, the model learned that breaking problems down, checking intermediate steps, and backtracking on dead ends leads to more rewards. The "reasoning ability" is a learned policy for producing useful token trajectories — not an internal cognitive faculty.

When you see "Extended Thinking" or "Reasoning Mode," what's actually happening: the application gives the model permission to write on scratch paper before handing in the exam. It's still writing. Still tokens. Still context. The entire thinking revolution is an application-level trick combined with post-training RL that encourages productive scratchpad use.

## the key insight: fixed compute per token

Here's the thing most people miss.

The forward pass of an LLM — the computation that produces each token — is a matrix multiplication through the layers of the network. And critically, **every token gets the exact same amount of compute, regardless of how hard the problem is.** The model spends identical effort producing "the" as it does producing the pivotal word in a complex reasoning chain.

Now consider: "I'm in Amsterdam, tell me how to get to Guatemala in three words."

You're asking the model to compress an enormous reasoning challenge — geography, logistics, transportation, ocean crossings — into three tokens. Three forward passes. Three identical chunks of compute. That's an impossible intelligence waterfall. The model can't build the reasoning needed, so it just outputs the three tokens that are most statistically plausible. The result is shallow at best.

But ask: "Plan step by step how to get from Amsterdam to Guatemala."

Everything changes. The model produces: "Let's think about this step by step. The user is in Amsterdam. Guatemala is in Central America. We need to cross the Atlantic..." Each token is trivially easy to predict given the previous ones. You've built **little bridges** — each generation step is a small, high-probability leap instead of one impossible jump.

**This is the entire reason chain-of-thought works.** More tokens = more forward passes = more compute = more little bridges of easy predictions instead of impossible leaps. It's not magic. It's giving the model scratchpad space to decompose hard problems into sequences of easy ones.

## persistence: memory for the memoryless

Because the context window is finite, the model can't think internally, and we need those little bridges — the natural conclusion is: **persist the work outside the model.**

This is where context engineering becomes a craft.

Create an `analysis_template.md`: "Your goal is X. Consider: problem statement, background, image of success, method, evidence, risks." Hand it to an agent. You've pre-built the bridges. The model doesn't need to figure out *how* to think about the problem — it's already contextualized with a structure that matches patterns from training data. "Problem statement: ..." → trivially easy to continue. "Evidence: ..." → the model knows exactly what comes next.

The template decomposes an ambiguous task into tractable steps — the little bridges from the previous section. And because it lives in a file, it's reusable across sessions without burning tokens.

This extends everywhere. SOUL.md files capture preferences so the model doesn't re-learn you every conversation. CLAUDE.md files define project conventions. Conversation summaries compress 100K tokens of history into 2K of essential context. Structured output from previous runs becomes input for the next.

The model is stateless. The system doesn't have to be.

## tools are just context

When you give an LLM "tools" — web search, code execution, APIs — you're not giving it abilities. You're adding structured text to the context.

A tool definition is a JSON schema in the prompt. The model doesn't "have" a web search tool; it sees `{"name": "web_search", "parameters": {"query": "string"}}` and produces tokens matching that format. The runtime intercepts those tokens, executes the function, and appends results to the context. That's the entire loop.

This is why MCP (Model Context Protocol) matters — it standardizes how tool schemas enter the context. And why 60 tools from 6 servers can consume 47,000 tokens just in definitions. Tools compete for context space like everything else. The model didn't gain 60 abilities; it received 47,000 tokens of structured text that bias predictions toward function-call patterns.

"Tool-calling" is pattern matching against schemas. "Agentic behavior" is a loop that appends observations and asks for the next action. There is no agency. There is context.

## the context paradox

Everything above builds toward one conclusion: context is everything. And it is. But there's a counterintuitive failure mode that catches every production team eventually: **more context can make your model dumber.**

Attention is zero-sum. When you add tokens, every existing token gets proportionally less attention. Stuff a retrieval system's top 100 results into the context and the model doesn't get smarter — it gets distracted. Stanford and Meta researchers showed that accuracy on multi-document QA actually fell *below closed-book performance* — no context at all — when relevant information was buried in the middle of the window. Adding context made it worse than having none.

Microsoft's Azure SRE team learned this the hard way. They built an agent for production incident response starting with 100+ specialized tools and 50+ agents. It was brittle — competent only on pre-encoded scenarios, with an ever-growing backlog of edge cases. The fix wasn't more tools. It was fewer: they collapsed everything into a handful of wide tools (Azure CLI, kubectl) and a few generalist agents. Less context, more capability. The models already knew these CLIs from training data — the team just needed to stop drowning that knowledge in tool definitions.

Context engineering isn't maximizing what goes in. It's minimizing what doesn't need to be there.

## position matters

And what does go in needs to go in the right place. LLMs have a U-shaped attention bias: strong attention to the beginning and end, weak in the middle. Recent research shows this is an inherent geometric property of causal attention — present even before training, baked into the architecture.

If critical information lands in the middle of a long context, the model underweights it. This is why production agent frameworks deliberately rewrite a `todo.md` at every step — pushing objectives to the end where attention is strongest. It's why system prompts go at the beginning. It's why your most important retrieval results should be first or last, never buried.

Context engineering isn't just about *what* goes in — it's about *where*.

## the retrieval revolution: Acc@1 → Acc@100

Ten years ago in search, you needed precision at rank 1. The user types a query, sees the first result — it better be right. Getting from a billion documents to the one correct answer was the entire problem.

LLMs changed this completely. You no longer need Acc@1 from your retrieval system. You need Recall@100. Get the 100 most relevant documents — semantic search handles this well: embeddings, approximate nearest neighbors, it scales from billions to hundreds efficiently. But 100 to the precise 3 that actually answer the question? Semantic similarity is too noisy. The ranking is approximate. Nuance is lost.

This is exactly where LLMs shine. Give a model 100 candidates and ask "which actually answer the question?" — that's a high-probability prediction. The model was trained on exactly this: reading text, understanding relevance, synthesizing answers.

The two-stage architecture — broad retrieval + LLM synthesis — is the foundation of every serious RAG system. And it works because someone understood the strengths and limitations of both systems and engineered the handoff.

## what's next

If you've followed this arc, you see the pattern: every context engineering technique is a workaround for a fundamental constraint. Statelessness → persistence. Finite context → compression and selection. Fixed compute → chain-of-thought. No thinking → scratchpad. Too much context → curation and positioning.

Frontier labs are attacking these constraints at the architecture level. CODA (2026) allocates more compute to harder tokens and less to easy ones — reducing cost 60% on simple problems while maintaining accuracy on hard ones. If this works at scale, chain-of-thought becomes optional rather than necessary. MemArt stores memories directly in the model's KV-cache representation — 100x fewer tokens than text-based retrieval, nearly matching full-context performance. If this matures, statelessness softens dramatically. Google's Infini-attention compresses old attention states into a memory bank for theoretically unbounded input. Ring Attention distributes sequence processing across devices without approximation.

None of these are solved. But notice: every one attempts to push into the architecture what we currently do at the application layer. Context engineering is the bridge between what models can do today and what they might do natively tomorrow.

## the real skill

Everyone is debating which model is best. GPT-5.4 vs Claude 4.6 vs Gemini 3.1. Benchmarks, leaderboards, vibes.

The real leverage is in what you feed it.

The model is the engine. Context is the steering wheel, the map, and the road. A mediocre model with great context will outperform a frontier model with bad context. I've seen this repeatedly in production.

Context engineering is not prompt engineering. Prompt engineering is writing a good sentence. Context engineering is building the entire information system that surrounds every inference call — memory, retrieval, tool schemas, conversation history, structured templates, compression, positioning — with the same rigor you'd bring to a database schema or API design.

This is the real skill of the AI age. And it starts with understanding what actually happens when you press Enter.
