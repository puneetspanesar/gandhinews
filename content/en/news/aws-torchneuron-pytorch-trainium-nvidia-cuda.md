---
id: aws-torchneuron-pytorch-trainium-nvidia-cuda
lang: en
type: news
section: science
format_label: "Science & Tech / AI"
topics: []
title: "Amazon releases TorchNeuron to lure AI start-ups from Nvidia to its Trainium chips"
standfirst: "The PyTorch-based tool lets developers move AI apps to Amazon's own chip by changing one line of configuration, the company says, in its most direct challenge yet to Nvidia's CUDA software."
published: 2026-10-20T02:00:00+05:30
keyPoints:
  - "TorchNeuron lets PyTorch apps run on **Amazon's Trainium chip**."
  - "AWS says porting needs **one line of configuration** and no code rewrite."
  - "Customer Deepgram says it now processes **70% more audio per dollar**."
hero:
  need: "Amazon's Trainium AI chip, or an Amazon Web Services data centre or office"
  suggested_source: "AWS Trainium chip"
  subjects: ["Amazon Web Services"]
  alt: "An Amazon Web Services Trainium chip (file photo)"
  overlay:
    value: "One line of code to leave Nvidia?"
related: [microsoft-unveils-maia-300-ai-chip, nvidia-joins-open-data-centre-design-standard, tenstorrent-raises-1-5-billion-6-2-billion-valuation]
seo:
  description: "AWS has released TorchNeuron, a PyTorch-based tool to move AI apps to its Trainium chip with a one-line configuration change, taking aim at Nvidia's CUDA."
sources:
  - title: "Amazon is taking its biggest shot at Nvidia yet with new TorchNeuron dev tool"
    publisher: "TechCrunch"
    date: 2026-10-19
    url: "https://techcrunch.com/2026/10/19/amazon-is-taking-its-biggest-shot-at-nvidia-yet-with-new-torchneuron-dev-tool/"
    primary: false
verification:
  status: approved
  notes:
    - "Single source (TechCrunch, Oct 19 1:09 pm PDT). Colin Brace quotes as given there."
---

Amazon Web Services has released a developer tool designed to make it easy for AI start-ups to move their software off Nvidia's chips and on to Amazon's own, its most direct attempt yet to weaken the hold of Nvidia's CUDA software on the industry.

The tool, TorchNeuron, is adapted from PyTorch, the free, open-source toolkit for building and running AI models. Amazon says about **85%** of AI apps are written with PyTorch. Because Nvidia has long made sure CUDA supports PyTorch apps well, its graphics chips have become the default choice for running them.

According to Amazon, moving a PyTorch app to Trainium, the AI chip made by its Annapurna Labs unit, now takes a change to one line of configuration and no rewriting of code. The company also says it will contribute code to the main PyTorch project to strip out parts that tie it to specific chips.

"The real story is removing the lock-in that kept developers from having a real choice at all," said Colin Brace, vice-president of technology software at AWS Annapurna Labs. He said Trainium's value was "price-performance plus the fact that it's one platform for both training and inference".

AWS pointed to Deepgram, an AI voice company, which it said now processes **70% more audio per dollar** after moving to Trainium.

The pitch is aimed partly at neoclouds such as CoreWeave and Nebius, many of which are built around Nvidia hardware. "You're building on AWS. You're not betting on a single-purpose compute provider," Brace said.
