---
id: anthropic-claude-formal-proofs-123-open-source-libraries
lang: en
type: news
section: science
format_label: "Science & Tech / AI"
topics: []
title: "Claude writes 180 million lines of proofs to show 123 open-source libraries cannot crash"
standfirst: "Anthropic and verification firm Theorem say the AI model proved memory safety at the machine-code level for code that runs across the internet, and found hundreds of bugs that years of testing had missed."
published: 2026-10-23T06:40:00+05:30
location: San Francisco
keyPoints:
  - "Claude produced formal proofs for **239 entry points in 123 libraries** tested by Google's OSS-Fuzz."
  - "The work ran to about **180 million lines** of proofs checked by the Rocq proof assistant."
  - "Along the way it found **hundreds of bugs**, including a known flaw in the libexpat XML parser."
hero:
  need: "Anthropic chief executive Dario Amodei, or Anthropic's offices in San Francisco"
  suggested_source: "Dario Amodei"
  subjects: ["Dario Amodei"]
  alt: "Anthropic chief executive Dario Amodei (file photo)"
  overlay:
    value: "180 million lines of proof"
related: [php2shell-flaws-governments-take-websites-offline, anthropic-claude-duet-proactive-agent]
seo:
  description: "Anthropic says Claude, working with Theorem, formally verified 123 open-source libraries at the RISC-V machine-code level and found hundreds of bugs missed by fuzz testing."
sources:
  - title: "LLMs are making formal software verification feasible at a much larger scale"
    publisher: "Anthropic"
    date: 2026-10-22
    url: "https://www.anthropic.com/research/formal-verification"
    primary: true
  - title: "Claude digs up bugs that survived trillions of tests across open-source software"
    publisher: "Interesting Engineering"
    date: 2026-10-22
    url: "https://interestingengineering.com/ai-robotics/claude-formal-verification-software-security"
    primary: false
verification:
  status: approved
  notes:
    - "All facts from Anthropic's research post (Oct 22, Frontier Red Team with Theorem) and Interesting Engineering (Oct 22, 6:10 pm EST = 4:40 am IST Oct 23). Published 6:40 am IST as Friday-morning India coverage."
    - "The post says 'over 100' in its summary and 123 in the body; 123 used. Libraries behind most bugs are not named in the post, so none named except libexpat."
    - "CVE number for libexpat flaw given in the post but not used in copy."
    - "Efficiency figures (Opus 5.5 vs Opus 5, 40% fewer tokens on half of 36 tasks) not used; kept the copy on the main result."
    - "No named Anthropic or Theorem spokesperson quoted in either source; quotes are from the post text itself."
---

Anthropic says its Claude model has written mathematical proofs that 123 widely used open-source software libraries will not crash on memory errors, checked right down to the machine code, in what the company calls "the first large-scale effort to use AI to apply formal verification to production software at the assembly code level."

The work, published by Anthropic's Frontier Red Team with the verification start-up Theorem, covered 239 fuzz-test entry points in libraries tested by OSS-Fuzz, Google's programme for continuously bombarding open-source code with random inputs. Over a few weeks Claude produced about 180 million lines of proof in Rocq, a proof assistant that checks each step mechanically. A typical proof ran to about 600,000 lines for a program with a median of 18,000 RISC-V instructions.

What it proved is narrow but strong. Each program, the post says, "will always exit normally without triggering memory-safety errors or failing assertions" for any input under 64 MB, assuming a single-threaded static binary running on a RISC-V processor under Linux.

## The bugs that testing missed

Getting there meant fixing the code first. Claude patched what it found and then proved the patched version, and the team says **hundreds of bugs** surfaced on the way, some of which had survived trillions of automated test runs.

Among them were a counter underflow in a decompressor that could cause an out-of-bounds write, but only on a rare input of about 20 MB, and an image decoder flaw that needed a 64 MB input and more than 2 GB of memory to show itself. Another out-of-bounds read appeared only after a particular sequence of calls on two handles to the same file. Claude also rediscovered a known vulnerability in libexpat, the XML parser, which required deeply nested input.

Not every problem was a crash. In one library a feature meant to restrict which files an application could load was not always enforced. In a separate effort on a PDF reader, the team says it found as many security bugs in one week as are usually reported in a year.

The work also included proofs that the Linux kernel's zlib compression code matches the formal standard for the format at the x86 binary level.

## What it does not mean

Anthropic is careful to say that "formally verified" is not the same as bug-free. A proof is only as good as its specification and its model of the machine. The proofs assume musl libc on RISC-V, while most of the world's servers and phones run x86 or ARM with glibc. Not every entry point was verified, and dead code and misuse by callers are outside the guarantee.

The team also watched for a familiar AI failure: Claude could have satisfied a proof simply by rewriting a program so that it never crashes because it never does anything. Patches were penalised, logged and audited to prevent that.

Cost remains the main limit, since a single proof can consume hundreds of millions of tokens. Anthropic expects better models and reusable proofs to bring that down.

A subset of the proofs and Theorem's RISC-V and Linux semantics have been released on GitHub. Proofs that could point attackers to bugs not yet patched are being held back. The release comes in a week when flaws in PHP pushed several governments to take websites offline.
