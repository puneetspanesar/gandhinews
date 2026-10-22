---
id: nvidia-gtc-berlin-openshell-agent-safety-dsx-pod
lang: en
type: news
section: science
format_label: "Science & Tech / AI"
topics: []
title: "Nvidia builds a hardware 'guard' for AI agents, with Anthropic and OpenAI on board"
standfirst: "At its Berlin conference, the chipmaker set out a design that watches AI agents from outside the system they run on, and a packaged 'AI factory' it says can be set up in about two weeks."
published: 2026-10-21T17:10:00+05:30
location: Berlin
keyPoints:
  - "Nvidia's **OpenShell Reference Architecture** puts a separate chip in charge of policing what AI agents do."
  - "Its Sentry monitor can stop an agent that breaks its limits **within milliseconds**, Nvidia says."
  - "A new modular data centre design, DSX POD, cuts set-up time to **about 14 days**, from about six months."
hero:
  need: "Nvidia BlueField data processing unit chip"
  suggested_source: "Nvidia BlueField DPU"
  subjects: ["Nvidia BlueField"]
  alt: "An Nvidia BlueField data processing unit (file photo)"
  overlay:
    value: "A guard chip for AI agents"
related: [nvidia-joins-open-data-centre-design-standard, google-torchtpu-open-source-pytorch-nvidia, aws-torchneuron-pytorch-trainium-nvidia-cuda]
seo:
  description: "Nvidia unveils OpenShell Reference Architecture at GTC Berlin to monitor AI agents from BlueField-4 chips, backed by Anthropic, OpenAI and Google, plus DSX POD."
sources:
  - title: "Nvidia OpenShell gets a hardware stack for Anthropic and OpenAI agents"
    publisher: "The Next Web"
    date: 2026-10-21
    url: "https://thenextweb.com/news/nvidia-openshell-ai-agents-safety-anthropic-openai"
    primary: false
  - title: "AI News Today, October 21"
    publisher: "AI Weekly"
    date: 2026-10-21
    url: "https://aiweekly.co/ai-news-today"
    primary: false
verification:
  status: approved
  notes:
    - "OpenShell details and Huang quotes from The Next Web (11:21 UTC, 21 Oct). DSX POD details and Huang's 'tokens' remark from the AI Weekly digest only; kept brief."
    - "Performance claims (milliseconds, up to 20% capacity) are Nvidia's own and attributed."
---

Nvidia wants the safety controls for AI agents to sit in the hardware, not just in software that the agents themselves might tamper with. At its GTC conference in Berlin on Wednesday, the chipmaker unveiled what it calls the OpenShell Reference Architecture, a design for running AI agents under limits enforced by a separate chip.

"Safety and control must be built into the computing architecture," said Jensen Huang, Nvidia's founder and chief executive. "With the OpenShell Reference Architecture, agents can think on Rubin, act on Vera and be governed on BlueField."

In plain terms, the AI models run on Nvidia's Vera Rubin systems and the agents' tools run on its Vera processors, while a BlueField-4 data processing unit runs a monitor called Sentry that watches the agents from outside. Nvidia says Sentry can quarantine and stop an agent that tries to step outside its boundaries within milliseconds, and can raise agent capacity by up to 20%.

Agents from Anthropic, OpenAI, Google, Meta, Cohere, Perplexity and others can run on the system. Anthropic has paired its Claude Managed Agents with OpenShell since September to limit and log what they do. Security companies including CrowdStrike, Palo Alto Networks, Okta and Zscaler are adding support, and SAP and ServiceNow are building it into their own agent products. Nvidia did not disclose prices.

The company also showed DSX POD, a modular, containerised design for an AI data centre built on Vera Rubin. Nvidia says it cuts the time to get one running from about six months to about 14 days.

"AI capability and safety must advance together," Huang said.
