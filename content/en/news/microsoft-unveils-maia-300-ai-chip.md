---
id: microsoft-unveils-maia-300-ai-chip
lang: en
type: news
section: science
format_label: Science & Tech / AI
topics: []
title: "Microsoft unveils Maia 300 chip to run its AI services and lean less on Nvidia"
standfirst: "The third-generation in-house accelerator will become the main engine behind Copilot and other Microsoft AI products from 2027, the company says."
published: 2026-10-13T03:00:00+05:30
location: Redmond
keyPoints:
  - "Microsoft says Maia 300 handles **40% more AI tokens per megawatt** than leading GPU systems."
  - "It will be the **primary inference chip** for Microsoft products from 2027."
  - "Nvidia and AMD chips will still be used to **train large AI models**."
hero:
  need: "Microsoft campus in Redmond, Washington, or a Microsoft data centre"
  suggested_source: "Microsoft Redmond campus building"
  alt: "Microsoft's campus in Redmond, Washington"
  overlay:
    value: "Microsoft's own AI chip, round three"
related: [nadella-ai-models-insider-risk-emergency-brake, openai-brings-gpt-6-to-all-chatgpt-users]
seo:
  description: "Microsoft unveils Maia 300, its third-generation AI chip, claiming 40% more tokens per megawatt than GPUs. It will power Copilot from 2027 at gigawatt scale."
sources:
  - title: "Microsoft moves to reduce Nvidia dependence with new Maia 300 AI chips"
    publisher: "Tech Startups"
    date: 2026-10-12
    url: "https://techstartups.com/2026/10/12/microsoft-moves-to-reduce-nvidia-dependence-with-new-maia-300-ai-chips-shifts-more-ai-workloads-in-house"
    primary: false
  - title: "Microsoft unveils Maia 300 custom AI chip"
    publisher: "Mobile World Live"
    date: 2026-10-12
    url: "https://www.mobileworldlive.com/ai-cloud/microsoft-unveils-maia-300-custom-ai-chip"
    primary: false
  - title: "Microsoft Announces Maia 300 AI Chip, Multi-Gigawatt Azure Scale-Up"
    publisher: "Unite.AI"
    date: 2026-10-12
    url: "https://www.unite.ai/microsoft-announces-maia-300-ai-chip-multi-gigawatt-azure-scale-up/"
    primary: false
verification:
  status: approved
  notes:
    - "Microsoft's own blog post by Scott Guthrie was not opened; his quotes come via Tech Startups and Mobile World Live, which match."
    - "Technical specs (TSMC N2P, eight HBM4 stacks, 950 W, 167 kW rack) are from Unite.AI only."
    - "Reuters figure of possibly more than 1 million chips next year is via Mobile World Live; left out of copy as unconfirmed by Microsoft."
    - "All performance figures are Microsoft's claims, not independently tested; said so in copy."
---

Microsoft has unveiled the third generation of its home-grown artificial intelligence chip, the Maia 300, and says it will become the main system running AI features across its products from next year, a step that would make the company less dependent on buying processors from Nvidia.

Scott Guthrie, Microsoft's executive vice-president for cloud and AI, announced the chip in a blog post on Monday. "As we move into the era of Super Intelligence, Microsoft is entering a new phase of infrastructure," he wrote. "We will scale our Azure Maia family to multi-gigawatt deployments starting in 2027, making Maia the primary inference system for Microsoft products and services."

## What the chip does

Inference is the work an AI model does each time someone uses it, such as answering a question in Copilot. Microsoft says Maia 300 was built for this job, with what Guthrie called "an inference-first architecture optimized for long-context, memory-intensive and decode-heavy AI workloads".

The company claims the chip processes 40% more AI tokens per megawatt of power than leading GPU-based systems, though it did not name Nvidia. A rack of 96 Maia 300 chips, it says, can handle up to seven times as many tokens as a rack built on the Maia 200, which arrived in January. Each rack also holds twice as many accelerators as before.

The compute parts of the chip are made on TSMC's N2P process and paired with eight stacks of HBM4 memory. Microsoft designed the silicon, racks, networking and data centres together as one system.

## Why power matters

Microsoft frames the gains in terms of electricity as much as speed. "We need new architectures that will give us essentially better performance, better use of the power that we have," said Alistair Speirs, a general manager at Microsoft. "You can think of power translating pretty directly into operational cost for something like a data center as well."

The Maia 200 already runs live work, including Microsoft 365 Copilot and OpenAI models on Azure. Satya Nadella, Microsoft's chief executive, told analysts in July that it delivered "30% better performance per dollar than the latest generation hardware in our fleet".

## Nvidia still in the picture

Microsoft will keep using Nvidia and AMD processors to train large models. Unlike the custom chips from Google and Amazon, Maia is not yet available for outside customers to rent through Azure.

All the performance figures so far are Microsoft's own. "Nobody has tested them outside of Microsoft yet," said Patrick Moorhead, chief executive of the research firm Moor Insights and Strategy.
