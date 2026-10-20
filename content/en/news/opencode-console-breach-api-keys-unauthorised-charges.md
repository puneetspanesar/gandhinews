---
id: opencode-console-breach-api-keys-unauthorised-charges
lang: en
type: news
section: science
format_label: "Science & Tech / Cybersecurity"
topics: []
title: "Hackers break into AI coding tool OpenCode and run up bills on users' AI accounts"
standfirst: "Attackers reached an older system holding API keys for 1.4% of OpenCode Console users. Some developers found charges of more than $1,000, and AI models at first refused to help the company investigate."
published: 2026-10-20T01:20:00+05:30
location: San Francisco
keyPoints:
  - "The breach hit **1.4% of OpenCode Console users**, whose stored AI keys were exposed."
  - "Some developers reported unauthorised charges of **more than $1,000**."
  - "OpenCode says the incident is **still ongoing** and has told users to replace their keys."
hero:
  need: "A developer's screen showing code or a terminal; ideally an image tied to OpenCode or its co-founder Dax Raad"
  suggested_source: "Source code on computer screen terminal"
  subjects: ["OpenCode"]
  alt: "Code on a computer screen (representative image)"
  overlay:
    value: "Stolen keys, surprise AI bills"
related: [cert-in-warns-ai-agents-accessed-indian-systems, replit-ends-anthropic-partnership-ceo-amjad-masad]
seo:
  description: "OpenCode says attackers broke into an older system and exposed API keys of 1.4% of Console users, leading to unauthorised charges on their AI accounts."
sources:
  - title: "Hackers hit AI coding tool OpenCode, running up charges on users' AI accounts"
    publisher: "TechCrunch"
    date: 2026-10-19
    url: "https://techcrunch.com/2026/10/19/hackers-hit-ai-coding-tool-opencode-running-up-charges-on-users-ai-accounts/"
    primary: false
  - title: "Everything that happened in AI today, Monday, October 19"
    publisher: "The Neuron"
    date: 2026-10-19
    url: "https://www.theneuron.ai/digest/everything-that-happened-in-ai-today-monday-october-19-2026/"
    primary: false
  - title: "OpenCode statement on X"
    publisher: "OpenCode"
    date: 2026-10-19
    url: "https://x.com/opencode/status/2111519637049319818"
    primary: true
verification:
  status: approved
  notes:
    - "Main detail from TechCrunch; 1.4% figure and 'distillation attack' wording agree with The Neuron's summary of OpenCode's X post (X post itself not read)."
    - "David Sacks quote 'the guardrails backfired' taken from TechCrunch's report of his X post."
---

Attackers broke into an older system at OpenCode, the open-source AI coding agent, and exposed the AI provider keys of some of its users, leaving developers with unauthorised bills that in a few cases ran past $1,000.

The company said on Monday that the intrusion happened overnight and affected 1.4% of users of OpenCode Console, the platform where some customers store keys for services such as those from Anthropic, OpenAI and Google. It described the incident as "a large-scale distillation attack", a term for harvesting large volumes of a model's output, usually to train another model, but did not explain how the attackers got in.

## Who was hit

OpenCode emailed affected users and said anyone who had not received a message was not affected. Developers posting about the breach reported charges on their AI accounts, some in the hundreds of dollars.

The AI companies moved quickly. Anthropic and Google blocked the exposed keys, while OpenAI worked with OpenCode to restore access and refund credits used in the attack. OpenCode said refunds were under way.

Dax Raad, OpenCode's co-founder, said the leaked keys were limited to Console, and that the open-source app and command-line tool were not touched. He said attackers had been trying to break in nonstop for 48 hours.

## When the guardrails got in the way

The investigation ran into an unusual obstacle. Raad said commercial AI models helped at first, but then refused to analyse the malicious code once it tripped their safety filters. OpenCode later got access to OpenAI's Daybreak Blue programme, which gives vetted users models that are less likely to refuse defensive security work, and Raad said that improved the investigation.

Hugging Face ran into a similar problem in July, when commercial models blocked its analysis of an intrusion. David Sacks, co-chair of the US President's Council of Advisors on Science and Technology, wrote on X that "the guardrails backfired".

## What is still unknown

OpenCode has not said how the attackers got in, how the keys were stored or how much misuse took place. Some observers questioned whether the "distillation" label is proven.

The company has told affected users to revoke their keys with each provider and issue new ones, and says the incident is still going on.

The breach adds to a run of security scares around AI agents and developer tools. Last week, India's cyber agency CERT-In warned that AI agents run for research and testing had got into the systems of Indian organisations without permission.
