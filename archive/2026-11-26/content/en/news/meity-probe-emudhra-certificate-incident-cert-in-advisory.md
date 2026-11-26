---
id: meity-probe-emudhra-certificate-incident-cert-in-advisory
lang: en
type: news
section: policy
format_label: "Policy / Cyber security"
topics: []
title: "MeitY opens probe into eMudhra certificate keys as CERT-In issues advisory"
standfirst: "The certifying authority says a flaw generated weak cryptographic keys in a small part of its international business. Its Indian digital signature and eSign services are said to be unaffected."
published: 2026-10-21T20:55:00+05:30
location: New Delhi
keyPoints:
  - "eMudhra reported that private keys of **eight intermediate certificates** in its PKI were compromised."
  - "Six were **TLS certificates** for websites and two were **code-signing** certificates."
  - "The company says the affected business brings in **about 1% of its revenue** and no customer data was exposed."
hero:
  need: "Electronics Niketan, the MeitY and CERT-In building on CGO Complex, New Delhi"
  suggested_source: "Electronics Niketan New Delhi"
  subjects: ["Electronics Niketan"]
  alt: "Electronics Niketan in New Delhi, home of the Ministry of Electronics and Information Technology"
  overlay:
    value: "Eight certificate keys compromised"
related: [cert-in-warns-ai-agents-accessed-indian-systems]
seo:
  description: "MeitY began a probe on October 21 after eMudhra reported compromised keys for eight intermediate certificates; CERT-In issued a mitigation advisory."
sources:
  - title: "MeitY launches probe into eMudhra certificate incident; CERT-In issues mitigation advisory (IANS)"
    publisher: "Punjab Kesari (English)"
    date: 2026-10-21
    url: "https://english.punjabkesari.com/business/meity-launches-probe-into-emudhra-certificate-incident-cert-in-issues-mitigation-advisory/"
    primary: false
verification:
  status: approved
  notes:
    - "Single source (IANS via Punjab Kesari, 8:45 pm), which in turn cites unnamed government sources reported by NDTV Profit for the 'limited and temporary' impact and DSC/eSign being unaffected; hedged as 'officials were reported to have said'. No named official quote."
    - "CERT-In advisory text not read directly; mitigation steps not listed in source, so not described."
    - "eMudhra HQ city not in source; not stated."
---

The Ministry of Electronics and Information Technology (MeitY) has opened an investigation into a security lapse at the digital certificate firm eMudhra, and the Indian Computer Emergency Response Team (CERT-In) issued a mitigation advisory on Wednesday.

eMudhra has reported that the private keys tied to eight intermediate certification authority certificates within its public key infrastructure were compromised. Six of them were **TLS certificates**, the kind that secure connections to websites, and two were code-signing certificates, which vouch that software comes from a trusted publisher.

## What went wrong

The company said a flaw in its system produced weak cryptographic keys alongside the strong ones it meant to create. A researcher alerted Apple, Google, Microsoft and Mozilla that the weak keys could potentially be worked out, including with AI-assisted techniques.

Security experts say compromised TLS keys could let an attacker issue fraudulent certificates for domains they do not control, impersonate genuine websites, and intercept or alter encrypted traffic. Code-signing keys could be misused to pass off malicious software as coming from a trusted source.

eMudhra said its infrastructure was not breached, no customer data was compromised and its physical and logical security controls remain intact. The problem, it said, was confined to a small part of its international TLS certificate business, which accounts for **about 1% of its revenue**, and did not touch its domestic digital signature operations.

## Government view

Officials were reported to have said the impact on Indian websites and apps was limited and temporary, and that eMudhra's India-regulated Digital Signature Certificate and eSign services were not affected. They cautioned against exaggerated claims on social media and said the ministry was also checking with other certificate operators. More details are expected once the investigation is complete.
