---
id: nvidia-joins-open-data-centre-design-standard
lang: hi
translation_of: nvidia-joins-open-data-centre-design-standard
type: news
section: science
format_label: विज्ञान-तकनीक / एआई
topics: []
title: "एआई डेटा सेंटर के साझा ब्लूप्रिंट पर एएमडी, गूगल और मेटा के साथ आई एनवीडिया"
standfirst: "चिप कंपनी अब एआई डेटा सेंटरों की बनावट, कूलिंग और बिजली व्यवस्था के एक खुले स्पेसिफ़िकेशन का समर्थन कर रही है, जब एक रैक की बिजली ज़रूरत एक मेगावाट की ओर बढ़ रही है।"
published: 2026-10-13T01:00:00+05:30
keyPoints:
  - "एनवीडिया **ओपन डेटा सेंटर स्पेसिफ़िकेशन** के संस्करण 0.7 से जुड़ गई है।"
  - "वह यह तय करने वाले मानक पर भी काम कर रही है कि डेटा सेंटर **बिजली की गड़बड़ी कैसे झेलें**।"
  - "ओपन कंप्यूट प्रोजेक्ट के मुताबिक़ प्रति रैक बिजली **1 मेगावाट पार करने** की राह पर है।"
hero:
  need: "एक बड़े डेटा सेंटर के अंदर सर्वर रैक की कतारें"
  suggested_source: "Open Compute Project server rack data center"
  alt: "डेटा सेंटर के अंदर ओपन कंप्यूट प्रोजेक्ट डिज़ाइन पर बने सर्वर रैक"
  overlay:
    value: "एआई डेटा सेंटरों का एक ब्लूप्रिंट"
related: [microsoft-unveils-maia-300-ai-chip]
seo:
  description: "एनवीडिया एएमडी, गूगल और मेटा के साथ ओपन डेटा सेंटर स्पेसिफ़िकेशन से जुड़ी, जो एआई डेटा सेंटरों की बनावट, कूलिंग और बिजली का खुला ब्लूप्रिंट है।"
sources:
  - title: "Nvidia, AMD, Google, and Meta team up on global blueprint for data center design"
    publisher: "Yahoo Finance"
    date: 2026-10-12
    url: "https://finance.yahoo.com/technology/article/nvidia-amd-google-and-meta-team-up-on-global-blueprint-for-data-center-design-150000023.html"
    primary: false
  - title: "Realizing the OCP Open Data Center Ecosystem Vision"
    publisher: "Open Compute Project Foundation"
    date: 2026-10-12
    url: "https://www.opencompute.org/news/realizing-the-ocp-open-data-center-ecosystem-vision/"
    primary: true
verification:
  status: approved
  notes:
    - "Nvidia's own announcement not found (newsroom had nothing after 8 Oct when checked). Nvidia's participation rests on Yahoo Finance; OCP post confirms the 'Open Data Center for AI' specification revision 0.7.0 but does not name Nvidia."
    - "Name differs: Yahoo says 'Open Data Center Specification v0.7'; OCP says 'Open Data Center for AI specification, Revision 0.7.0'. Used OCP's fuller name in body."
    - "Yahoo calls the grid standard 'OCP Grid Resilience Specification'; OCP describes an interface specification for disturbance performance between hyperscale data centres and the grid. Treated as the same work; flag if wrong."
    - "Yahoo's lines on New York and Texas data centre pauses left out (single source)."
---

एनवीडिया ने आर्टिफ़िशियल इंटेलिजेंस चलाने वाले डेटा सेंटरों के एक साझा, खुले डिज़ाइन के समर्थन में एएमडी, गूगल और मेटा का साथ पकड़ा है। यह डिज़ाइन बताता है कि इमारतें कैसे बनें, कैसे ठंडी रखी जाएँ और उन्हें बिजली कैसे मिले।

यह काम ओपन कंप्यूट प्रोजेक्ट (ओसीपी) के तहत हो रहा है, जो हार्डवेयर डिज़ाइन खुले तौर पर साझा करने वाला उद्योग समूह है। इसका ओपन डेटा सेंटर फ़ॉर एआई स्पेसिफ़िकेशन, जो अब संशोधन 0.7 पर है, एआई के लिए तैयार सुविधाओं का रोडमैप पेश करता है। एनवीडिया गूगल, मेटा और माइक्रोसॉफ़्ट के साथ एक अलग मानक पर भी काम कर रही है, जो तय करेगा कि बिजली ग्रिड में गड़बड़ी के दौरान बड़े डेटा सेंटर कैसे व्यवहार करें, जिसमें वोल्टेज गिरने पर चलते रहना और बाद में बिजली बहाल करना शामिल है।

एनवीडिया का कहना है कि ये स्पेसिफ़िकेशन सिस्टम बनाने वालों, कोलोकेशन प्रदाताओं और संचालकों को तैयार टेम्पलेट देते हैं, ताकि उन्हें हर ग्राहक के अलग कस्टम डिज़ाइन से न जूझना पड़े। तेज़ और एक जैसे निर्माण से एनवीडिया को अपनी चिप, सिस्टम और नेटवर्किंग उपकरण ज़्यादा बेचने में भी मदद मिलेगी।

## बिजली की समस्या

यह पहल ऐसे समय आई है जब एआई के कारण सर्वरों के हर रैक की बिजली ज़रूरत तेज़ी से बढ़ रही है। सोमवार को एक पोस्ट में ओसीपी के प्रमुखों ने कहा कि प्रति रैक बिजली घनत्व 1 मेगावाट तक पहुँचने और फिर उसे पार करने की राह पर है। समूह 800 वोल्ट डायरेक्ट करंट बिजली पर भी काम प्रकाशित कर रहा है, जिसे आगे 1,500 वोल्ट तक ले जाने की योजना है, साथ ही सॉलिड-स्टेट ट्रांसफ़ॉर्मर पर भी।

ओसीपी फ़ाउंडेशन के जेम्स केली, क्लिफ़ ग्रॉसनर और ज़ेन बॉल ने लिखा, "सीधे शब्दों में, यह चिप से ग्रिड तक डिज़ाइन, तैनाती और संचालन की एक बड़ी समस्या है।" उन्होंने लिखा, "हाइपरस्केल वह जगह है जहाँ नए आविष्कार जन्म लेते हैं और साबित होते हैं, जिसका फ़ायदा बाक़ी सबको मिलता है।"

फ़ाउंडेशन के मुताबिक़ रिसर्च फ़र्म आईडीसी का अनुमान है कि 2030 में ओसीपी-मान्य डिज़ाइनों पर बने आईटी उपकरणों पर 890 अरब डॉलर से ज़्यादा खर्च होगा।
