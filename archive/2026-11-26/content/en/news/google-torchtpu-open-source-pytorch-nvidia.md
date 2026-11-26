---
id: google-torchtpu-open-source-pytorch-nvidia
lang: en
type: news
section: science
format_label: "Science & Tech / AI"
topics: []
title: "Google opens up TorchTPU a day after Amazon, in a second swipe at Nvidia"
standfirst: "The open-source tool lets developers move existing PyTorch AI apps onto Google's own chips with a configuration change instead of a rewrite."
published: 2026-10-21T00:20:00+05:30
location: Mountain View
keyPoints:
  - "Google has released **TorchTPU**, its version of PyTorch for its own chips, as an open-source project."
  - "The move comes **a day after Amazon** launched TorchNeuron for its Trainium chip."
  - "Google says it worked with **Meta and Hugging Face**, among others, so the tool fits existing software."
hero:
  need: "Google Tensor Processing Unit (TPU) chip or board"
  suggested_source: "Google Tensor Processing Unit"
  subjects: ["Tensor Processing Unit"]
  alt: "A Google Tensor Processing Unit board (file photo)"
  overlay:
    value: "Now Google wants Nvidia's developers"
related: [aws-torchneuron-pytorch-trainium-nvidia-cuda, tenstorrent-raises-1-5-billion-6-2-billion-valuation, microsoft-unveils-maia-300-ai-chip]
seo:
  description: "Google released TorchTPU as open source, letting PyTorch AI apps run on its TPUs with a configuration change, a day after Amazon's TorchNeuron."
sources:
  - title: "Google has joined Amazon in attacking Nvidia's stronghold with AI app developers"
    publisher: "TechCrunch"
    date: 2026-10-20
    url: "https://techcrunch.com/2026/10/20/google-has-joined-amazon-in-attacking-nvidias-stronghold-with-ai-app-developers/"
    primary: false
verification:
  status: approved
  notes:
    - "Single source: TechCrunch, Oct 20, 11:38 am PDT (12:08 am IST Oct 21). No quotes from Google in source. The 85% PyTorch share is 'by some accounts' and is hedged in copy."
---

Google has made TorchTPU, its version of the PyTorch programming toolkit, available as an open-source project, a **day after Amazon** did the same for its own AI chip. Both companies want developers to stop writing AI software that runs by default on Nvidia's graphics processors.

PyTorch is the open-source toolkit most developers use to build, train and run AI models. By some estimates it sits under **85%** of AI applications. Meta, then Facebook, built it in 2016 and handed it to the Linux Foundation in 2022. Most PyTorch code, though, is tuned to run on Nvidia hardware.

TorchTPU lets that code run on Google's Tensor Processing Units. Google says developers can move an existing PyTorch app with a simple configuration change and no rewriting, which also makes it easy to shift the app onto Google Cloud.

Google said it worked directly with Meta, Hugging Face, Inferact, which makes the vLLM inference engine, RadixArk, maker of SGLang, and others to make sure TorchTPU works well with their tools. It has also launched a TPU agent suite to help developers move their apps across and fix errors on the way, and updated LiteRT, its software for running AI on phones, laptops and small devices, to handle PyTorch apps better.

Amazon's tool, TorchNeuron, does the same job for its Trainium chip on Amazon Web Services. Amazon says it is also sending code to the main PyTorch project to separate its features from Nvidia chips, so that PyTorch works with any hardware by default.

Developers are unlikely to abandon Nvidia en masse because of two new tools. But with two of the largest cloud companies now chipping away at the same advantage in the same week, the pressure on Nvidia's grip over AI software is growing.
