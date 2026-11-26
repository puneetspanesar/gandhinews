---
id: php2shell-flaws-governments-take-websites-offline
lang: en
type: news
section: science
format_label: "Science & Tech / Cybersecurity"
topics: []
title: "Governments pull websites offline as 'PHP2Shell' flaws expose the web's most common language"
standfirst: "Two critical bugs in PHP, found with the help of AI and hidden in the code for more than a decade, have pushed ministries, ports and hospitals in Europe offline while administrators rush to install emergency fixes."
published: 2026-10-22T17:30:00+05:30
location: The Hague
keyPoints:
  - "The two PHP flaws, nicknamed **PHP2Shell**, each scored 9.2 out of 10 for severity."
  - "The US National Security Agency advised taking sites **offline if they could not be patched at once**."
  - "Amazon says it saw an **exploit attempt on October 17**, before the flaws were made public."
hero:
  need: "The PHP programming language logo, or the Port of Rotterdam, one of the bodies that took its website offline"
  suggested_source: "PHP logo"
  subjects: ["PHP"]
  alt: "The logo of the PHP programming language"
  overlay:
    value: "Two bugs, a decade old, now critical"
related: [cert-in-warns-ai-agents-accessed-indian-systems]
seo:
  description: "PHP2Shell: two critical flaws in the PHP programming language led governments in the Netherlands, France, Germany, Finland and Belgium to take websites offline as patches were rushed out."
sources:
  - title: "World leaders warn of security flaws found in PHP programming language"
    publisher: "Al Jazeera"
    date: 2026-10-22
    url: "https://www.aljazeera.com/news/2026/10/22/world-leaders-warn-against-security-flaw-found-in-php-computer-programming"
    primary: false
  - title: "What's the PHP coding flaw that could pull down 70 percent of the internet?"
    publisher: "Al Jazeera"
    date: 2026-10-22
    url: "https://www.aljazeera.com/news/2026/10/22/whats-the-php-coding-flaw-that-could-pull-down-70-percent-of-the-internet"
    primary: false
verification:
  status: approved
  notes:
    - "Both sources are Al Jazeera pieces drawing on Reuters and AFP (Oct 22). PHP Foundation advisory, NSA notice, Wiz and Calif write-ups not read directly. No CVE numbers or patched version numbers in sources, so none given."
    - "NSA warning and patch release dated 'Wednesday' (Oct 21) in sources. Netherlands, Finland, Belgium, South Korea responses are from the updated Oct 22 explainer; exact hour of each takedown not given, so copy says 'this week'. Published time 5:30 pm IST is an estimate for when the wider government takedowns were being reported."
    - "Wiz described as owned by Alphabet/Google per sources. '70 percent' figure is from a headline only and is not used in the copy."
    - "No India-specific response (CERT-In) found in sources read; not mentioned."
---

Government departments across Europe have taken their websites offline after two critical flaws were found in PHP, the programming language behind a large share of the world's websites, and details of the bugs leaked before every server could be fixed.

The vulnerabilities, nicknamed PHP2Shell, let an attacker run commands on a server running affected PHP code without a password or an account. Each scored 9.2 out of 10, the "critical" band. They had sat in the code for more than a decade and affect PHP 5.4 and every later version, according to the security firms Calif, Wiz and Cloudflare.

The US National Security Agency issued a rare public warning on Wednesday, advising organisations to take sites offline if they could not update them immediately. The PHP Foundation, the non-profit that maintains the language with volunteers, released two patches the same day and told administrators they were "encouraged to update immediately".

## Who went dark

The Dutch national cybersecurity agency took its own website down as a precaution, and others followed: the Port of Rotterdam, the government portal Overheid.nl, the KNVB football association, the websites of the five largest political parties and several hospitals. Prime Minister Rob Jetten said he was following the situation closely.

In Finland, the state IT provider Valtori took government public network services offline. France's Interior Ministry put its sites, including those of local administrative offices, into preventive maintenance. Germany's digital ministry pulled some websites as a precaution, and Belgium's foreign affairs service went offline after reports of exploitation, although the national cybersecurity centre said it had recorded no attacks on Belgian sites. The Czech Republic also shut sites to patch them.

Outside Europe, South Korea raised its private-sector cyber alert level and sent guidance to about 28,000 companies. Japanese Prime Minister Sanae Takaichi used social media to warn about the risk. The Wikimedia Foundation took some systems down until they were patched, and the Internet Archive briefly went offline.

## Found with AI, leaked early

Calif, working with OpenAI, reported the first flaw on August 11, and Wiz reported the second on August 24. Both teams used AI tools in the search. Wiz said the findings "rank among the most severe vulnerabilities discovered in PHP".

The problem lies in how PHP handles fatal errors such as running out of memory. Wiz said this could also expose passwords and other credentials held in a server's memory.

The details leaked online on October 21, before fixes were ready. Amazon's security chief, CJ Moses, said the company had detected an attempt to exploit the bugs on October 17, before any public disclosure. How the attacker learned of them is not known.

Andrew Cullen, who lectures on AI and cybersecurity at the University of Melbourne, called the situation "really unprecedented". The PHP Foundation said it expects AI to make such weaknesses easier to find, and has asked large technology companies to coordinate their response.

Sites that have installed the updates are protected. The risk now sits with the many smaller, older installations that are rarely maintained.
