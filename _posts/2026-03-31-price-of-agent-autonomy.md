---
layout: post
title: "the price of agent autonomy"
description: "Autonomy and risk don't accidentally go together. They depend on the same permissions."
published: true
image: /assets/price-of-agent-autonomy/og-image.png
redirect_from:
  - /price-of-agent-autonomy/
---

Every capability you give an agent is also an attack surface.

You want it to move meetings, write code, send grandma photos from the kindergarten group, and build digital businesses while you're on the beach drinking a piña colada. But the same access that enables all of that enables things you didn't intend. That's not a bug in any particular system - it's the structural cost of autonomy. The more useful the agent, the more permissions it needs, the more damage it can do if something goes wrong.

Agent security is a massive open problem. Most of these systems feel like a security nightmare with a good UI. The defaults across the ecosystem are "full access, trust the model" - which is [L5 autonomy](https://asdlc.io/concepts/levels-of-autonomy/) - agents that hold credentials and act unsupervised 24/7 - with L0 security thinking.

So while the ecosystem matures and proper solutions are developed, here are the principles I apply when running agents on my own data.

## 1. trust your supply chain

One crooked `npm install` the agent naively runs is enough to slip in a prompt injection. The agent didn't mean to install something malicious - it was just following instructions. But now the photos from kindergarten aren't going just to grandma.

This is where software supply chain security meets agentic AI. I work at [JFrog](https://jfrog.com) - it's not a coincidence this is principle number one. Establishing trust in everything the agent consumes - packages, models, MCP servers, and skills - isn't optional hygiene when an autonomous agent is the one pulling dependencies instead of a human reading a lockfile diff.

This isn't hypothetical. On March 30, 2026, [axios](https://www.itnews.com.au/news/supply-chain-attack-hits-300-million-download-axios-npm-package-624699) - 300 million weekly downloads - was compromised through stolen maintainer credentials. The attacker bypassed CI/CD, manually published poisoned versions with a RAT dropper, and staged a clean decoy package first to avoid triggering scanners. If your agent auto-updated, it was owned.

An agent that can run arbitrary code and install arbitrary dependencies without supply chain verification is an agent that can be compromised by anyone who can get a malicious package into its path.

## 2. small code, less risk

The more code a library has, the harder it is to understand what it does and where the risks are. I prefer to read the source before handing over my keys.

This isn't about being anti-framework. It's about auditability. When you're giving something access to your credentials and your data, "I've read the code" is a security posture, not a hobby. [epsiclaw](/2026/03/25/epsiclaw/) exists because I wanted to understand what a personal AI assistant actually does at the algorithm level - 515 lines, not 500K.

Choose libraries you can audit. Understand what you're running before you give it `blind approve`.

## 3. understand the real security model

Not the README version. The actual architecture.

Is there container isolation? Is there a credentials proxy? Does the agent see the API keys directly, or does it request actions through a mediation layer? These details change the entire exposure profile.

A system where the agent holds your LLM provider's API key in an environment variable is fundamentally different from one where a [credential proxy](https://github.com/onecli/onecli) intercepts requests and injects the key at the HTTP level - where the key literally doesn't exist inside the container.

Ask these questions before you deploy:
- Where do credentials live at runtime?
- What can the agent read from the filesystem?
- What happens if the agent is prompt-injected?
- What's the blast radius of a compromised session?

## 4. egress filtering

If the agent should only talk to `jfrog.io`, `github.com`, `anthropic.com`, and `googleapis.com` - there's zero reason it should be open to the rest of the internet.

A prompt-injected agent with unrestricted network access can POST your files to any server. The credentials might be hidden behind a proxy, but your data isn't. A few domains in a proxy allowlist turns "can exfiltrate to anywhere" into "can exfiltrate to GitHub." Much better. Not zero, but much better.

Allowlist, don't blocklist. Start strict. Add domains when the agent hits errors, not before.

## 5. least privilege

Don't give "GitHub access." Give access to the specific repositories the agent needs. Not a pixel more.

Create fine-grained tokens scoped to individual repos with only the permissions required - Contents, Issues, Pull Requests. Create dedicated accounts where possible: a separate email, a dedicated SIM for communication channels. Every integration should be scoped to exactly what the agent needs to function, and nothing beyond.

The gap between "the agent has my GitHub account" and "the agent has write access to two repos" is the difference between losing everything and losing a branch.

## 6. choose your communication channel by blast radius

Telegram: each bot has its own identity and API key. If it gets compromised - delete the bot, create a new one, move on. Maximum damage: the bot's conversation history.

WhatsApp: no official SDK for private accounts. Most libraries rely on unofficial reverse-engineered protocols. The agent's identity is *your* identity. It has access to your messages, your contacts, everything you didn't intend to expose. If it gets compromised, the blast radius is your entire WhatsApp account.

Choose channels where the agent's identity is disposable and isolated from yours.

## no free lunch

There's more to add here - budget controls so the agent doesn't burn your entire API credit in its first hour, runtime monitoring, kill switches on a separate channel. And even with all principles applied, you won't reach 100% security. That's the no-free-lunch that comes with autonomy.

The goal isn't to avoid agentic AI. It's to adopt it from a position of knowledge - understanding what you have in your hands, what you gave it to make it work, and what the blast radius looks like if something goes wrong. Not to wake up one morning inside a crisis you didn't realize you'd walked into.

Autonomy and risk don't accidentally go together. They depend on the same permissions.
