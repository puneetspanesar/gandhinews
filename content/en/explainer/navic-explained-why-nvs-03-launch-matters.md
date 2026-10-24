---
id: navic-explained-why-nvs-03-launch-matters
lang: en
type: explainer
section: science
format_label: "Explained / Space"
topics: []
title: "NavIC explained: why India's own navigation system needs the NVS-03 launch"
standfirst: "ISRO will fly the NVS-03 satellite on a GSLV from Sriharikota on 30 October. What NavIC is, why failing clocks and a lost satellite left it short of a full service, and what one launch can fix."
published: 2026-10-24T11:10:00+05:30
shortAnswer: "NavIC is India's regional satellite navigation system, run by ISRO, which gives position and time over India and about 1,500 km beyond its borders without relying on GPS. Atomic clock failures on the first-generation satellites and the loss of NVS-02 in 2025 left it with three working satellites, one short of the four needed for standalone positioning. NVS-03, due on 30 October with an Indian-made rubidium clock, would bring it back to that minimum."
hero:
  need: "A PSLV or GSLV launch carrying a NavIC (IRNSS) satellite from Sriharikota"
  suggested_source: "IRNSS-1I PSLV-C41 launch"
  subjects: ["PSLV-C41"]
  alt: "A PSLV rocket lifts off from Sriharikota with a NavIC navigation satellite (file photo)"
  overlay:
    value: "Four satellites, or no fix"
related: [nvs-03-navic-satellite-gslv-launch-october-30, isro-gaganyaan-crew-service-module-separation-tests]
seo:
  description: "What NavIC is, how it differs from GPS, why clock failures and the NVS-02 loss weakened it, and why ISRO's NVS-03 launch on 30 October 2026 matters."
sources:
  - title: "ISRO to Launch NVS-03 on October 30"
    publisher: "Channel IAM"
    date: 2026-10-23
    url: "https://en.channeliam.com/2026/10/23/isro-nvs-03-navic-satellite-launch-october/"
    primary: false
  - title: "ISRO to Launch NVS-03 Navigation Satellite on October 30"
    publisher: "GKToday"
    date: 2026-10-22
    url: "https://www.gktoday.in/isro-to-launch-nvs-03-navigation-satellite-on-october-30/"
    primary: false
  - title: "NVS-03"
    publisher: "Wikipedia"
    date: 2026-10-23
    url: "https://en.wikipedia.org/wiki/NVS-03"
    primary: false
  - title: "NavIC"
    publisher: "Wikipedia (mirror)"
    date: 2026-10-24
    url: "https://wiki.riteme.site/wiki/NavIC"
    primary: false
verification:
  status: approved
  notes:
    - "30 October date, GSLV Mk II, 2,232 kg, rubidium clock from the Space Applications Centre, three working satellites and four-needed line, NVS-02 propulsion failure (January 2025): from the desk's 23 October news story and its sources (Channel IAM, GKToday, Wikipedia)."
    - "History (IRNSS-1A launched 1 July 2013, its three clocks failing from July 2016; nine of 24 clocks failed by May 2018; IRNSS-1H lost on PSLV-C39 on 31 August 2017 when the heat shield did not separate; IRNSS-1I on 12 April 2018; NVS-01 on 29 May 2023 with an indigenous clock and L1 signal), accuracy figures, L5/S bands, AIS 140 vehicle rule from 1 April 2019 and Qualcomm phone support: from a mirror of the Wikipedia NavIC page. That page's NVS-02 entry was out of date; the January 2025 failure is taken from the news story sources instead."
    - "Accuracy figures on the page vary (5-10 m over India in one place, 3 m in the infobox); copy uses the 5-10 m standard service figure only, loosely."
    - "Exact launch time not announced as of 24 October."
---

## What is NavIC?

**It is India's own satellite navigation system, built and run by the Indian Space Research Organisation.**

Its formal name is the Indian Regional Navigation Satellite System, or IRNSS; NavIC, short for Navigation with Indian Constellation, is the name it goes by in public. Like the American GPS, it uses satellites that broadcast very precise time signals. A receiver on the ground compares the signals from several satellites and works out where it is.

The difference is reach. GPS covers the whole planet. NavIC is regional: its main service area is India and roughly 1,500 km around its borders, which takes in much of the Indian Ocean. Its satellites sit high above the region in geostationary and inclined geosynchronous orbits, so they stay over the same part of the sky.

## Why does India need its own system?

**So that position and timing over the country do not depend on a system controlled by another government.**

Navigation signals guide aircraft, ships, trucks and missiles, and they keep power grids, telecom networks and banks in step. A country that relies wholly on GPS relies on the United States keeping it switched on and accurate. NavIC was built to give India a signal of its own, with an open service for civilians and a restricted, encrypted one for the armed forces.

The standard service is meant to fix a position to within about 5 to 10 metres over India. NavIC uses two frequency bands, L5 and S, which lets receivers measure the distortion caused by the upper atmosphere directly instead of estimating it.

## What went wrong?

**The clocks failed, and then a replacement satellite was lost.**

Each navigation satellite carries atomic clocks, and a satellite with no working clock cannot do its main job. The first NavIC satellite, IRNSS-1A, was launched on 1 July 2013 with three imported rubidium clocks. The first failed in July 2016 and the other two soon after. By May 2018, nine of the 24 clocks in orbit across the system had failed.

Replacing satellites proved hard too. IRNSS-1H, sent up in August 2017 to stand in for 1A, was lost when the heat shield on its PSLV rocket did not separate. IRNSS-1I reached orbit in April 2018. Then NVS-02, launched in January 2025, never reached its intended orbit because a propulsion problem stopped the manoeuvre that was to raise it there.

## How many satellites does NavIC need?

**At least four working ones to give a position on its own.**

A receiver needs signals from four satellites to work out its location in three dimensions and correct its own clock. NavIC currently has only three available for that service. With three, it cannot offer standalone positioning, and by late 2024 its use was largely confined to the armed forces.

```compare
{"title":"Two generations of NavIC satellites","columns":["IRNSS-1 series","NVS series"],"rows":[{"icon":"calendar-blank","label":"First launch","cells":["July 2013","May 2023"]},{"icon":"clock","label":"Atomic clocks","cells":["Imported rubidium; many failed","Rubidium clock built in Ahmedabad"]},{"icon":"wifi-high","label":"Signals","cells":["L5 and S bands","Adds a civil L1 signal for low-power devices"]},{"icon":"rocket-launch","label":"Rocket","cells":["PSLV","GSLV Mk II"]}]}
```

## What is new about NVS-03?

**It carries an Indian atomic clock and a signal designed for ordinary consumer devices.**

NVS-03 is the third of the second-generation NVS satellites and the twelfth spacecraft built for the system. It weighs 2,232 kg and is designed to work for 12 years from a slot at 32.5 degrees East. Its rubidium clock was developed by ISRO's Space Applications Centre in Ahmedabad, a direct answer to the failures of the imported clocks.

It also broadcasts on the L1 band, the frequency that GPS uses for its main civilian signal. That matters for phones, smartwatches and fitness trackers, which are built around L1 and struggle with NavIC's older L5 and S signals. The first NVS satellite, NVS-01, launched on 29 May 2023, introduced both the Indian clock and the L1 signal.

## Does my phone use NavIC?

**Possibly, if its chip supports it.** Some phones have been able to receive NavIC since 2020, through Qualcomm chipsets, and support for the L1 signal has been rolling out since. There is no rule requiring phones to carry it. Commercial vehicles are a different matter: since 1 April 2019 they have had to use NavIC-based tracking devices under the AIS 140 standard.

For most users, a phone combines signals from several systems at once, so a stronger NavIC adds accuracy and a backup rather than replacing GPS.

## What happens after the launch?

**If NVS-03 reaches its slot, NavIC is back to the minimum it needs.**

The launch on a GSLV Mk II from the Satish Dhawan Space Centre at Sriharikota had been aimed at mid-October, and before that at late 2025; ISRO has been cautious with its schedule after setbacks to the PSLV this year. Even a successful flight only restores the floor. NVS-04 and NVS-05 are being built, and ISRO's longer plan is to expand the constellation so that the loss of one satellite no longer puts the whole service at risk.
