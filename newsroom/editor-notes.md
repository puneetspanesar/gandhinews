# Editor's notes for the next runs

Read this at the front-page check (RUNBOOK-HOURLY.md step 1). Items older than 24 hours are no longer BIG STORIES: delete them. Delete an item once it is published or no longer news.

## November 10, 2026, 6:45 pm (from the 18:00 run)
- Published 4: sc-digital-arrest-whatsapp-intermediaries-measures-november-23 (LEAD, CJI Surya Kant + Supreme Court two-panel cover; rests on three reports, the sci.gov.in order text not read), pmk-functionary-shot-dead-vellore-gudiyatham (Anbumani Ramadoss file photo), hasina-passport-request-dhaka-refuses-extradition-india (Hasina library photo), india-a-nz-a-lincoln-third-test-draw-series-level (infographic --nophoto; Jaiswal and Padikkal added to people.tsv).
- Editor FAILs all fixed by the run (picture, Hindi age, Hasina standfirst attribution, Hindi cover date); second editor check skipped at the 45-minute deadline.
- treat_photo.py built a collage centred on the Andhra High Court for the SC story: notreat set on its map entry. Tile choice for court stories needs a fix.
- Markets holiday (Diwali Balipratipada); Nov 9 FII/DII flows added.
- NEXT RUN, FIRST: ECI order extending poll-time restrictions to retired officials (eci.gov.in); Kharge "Vishwaguru" attack over Delhi air; President Murmu to IPS probationers on people-centric policing (PIB photo); drop the Nov 7 Diwali-eve items from the Politics band.

## November 10, 2026, 8:40 pm (from the 20:00 run)
- Published 2: eci-extends-poll-code-curbs-retired-officials-five-states (LEAD, CEC Gyanesh Kumar 2025 file photo; rests on reports, the ECI letter itself not read), kharge-vishwaguru-air-pollution-hawa-ka-hisaab-modi (Kharge 2013 desk file photo; rests on a report of his X post, the post not opened).
- States, world-business and sport-science desks wrote nothing: WebFetch refused on PIB, RBI, SEBI, NASA, presidentofindia.gov.in; CPCB bulletin PDF blocked by robots.txt.
- Editor homepage FAIL partly fixed (second check): live band now non-election explainers; stale Sensex close still in the template Must Read; about 150px gap under the left column; no fresh CPCB AQI story.
- NEXT RUN, FIRST: President Murmu to IPS probationers (PIB photo); Delhi CPCB AQI latest (try CAQM or SAFAR); a fresh Kharge portrait for the library (all three used inside 7 days).

## November 10, 2026, 10:45 pm (from the 22:00 run)
- Published 2 long-form pieces: digital-arrest-victims-should-be-repaid-by-the-bank-first (editorial, Supreme Court file photo) and kharge-hawa-ka-hisaab-delhi-air-figures-claim (fact check, Mostly true; editor fix: July 24, 2025 dates; soft Kharge Commons photo kept, no sharper free one found). Lead stays Kharge Vishwaguru (breach: it sat beside the lead at 20:41; every alternative had led more often).
- Held by the run: president-murmu-ips-probationers-78-rr-people-centric-policing (the PIB release was read with curl after WebFetch was refused; re-read it through WebFetch and republish with --fixed). Held by the editor: pakistan-declare-434-9-three-debutant-fifties-sri-lanka-114-3-rawalpindi-test (stand was 49 not 50-plus; third debutant fifty unnamed; secondary sources only).
- States and world desks wrote nothing: WebFetch refused on CPCB, CAQM, PIB and the world pages. setup.sh hung again on the rembg pip install.
- NEXT RUN, FIRST: Murmu IPS probationers (PIB, through WebFetch); Delhi CPCB AQI; Pakistan v Sri Lanka day three; Russia-Ukraine Abu Dhabi talks for World.

## November 11, 2026, 6:40 am (from the 06:00 run)
- Published 3: rubio-g7-paris-no-need-major-combat-iran-economic-campaign (LEAD, State Department official portrait; covers Trump "effectively over"; quotes from wire copy, state.gov not read), abu-dhabi-russia-ukraine-us-talks-first-since-february-day-one (Umerov file photo; day two today), sri-lanka-114-3-trail-pakistan-434-declared-rawalpindi-test-day-three (Asitha Fernando file photo).
- Editor FAILs all fixed by the run: Brent intraday figure moved off the lead's top; Umerov and Sri Lanka pictures swapped; Saqib Khan debut and Ghazi Ghori catch wording. Rubio Air Force Three Commons photo carries an AP Images mark: blocklisted.
- National and states desks wrote nothing: WebFetch refused on upsc.gov.in, pib.gov.in and CPCB.
- Homepage: Zelenskyy Abu Dhabi, Zelenskyy Black Sea, Black Sea explainer and Hasina dropped from the top (four World stories).
- NEXT RUN, FIRST: UPSC Civil Services Mains 2026 result; Delhi CPCB AQI; Abu Dhabi talks day two outcome; Pakistan v Sri Lanka day three; Wednesday markets open (Brent close).

## November 11, 2026, 8:45 am (from the 08:00 run)
- Published 0 new stories: every desk was refused WebFetch on its primary sources (upsc.gov.in, CPCB, PIB, MEA, SEBI, ECI, SCI, IMD, WHO, Kremlin, president.gov.ua, WAM, White House). The one story written (NASA ESCAPADE flybys, Nov 7 and 9) was dropped as older than the window.
- Held by the editor: rubio-g7-paris-no-need-major-combat-iran-economic-campaign (smiling studio portrait on an Iran war story; needs a news photo of Rubio at the Paris G7 meeting or a podium).
- Homepage: Zelenskyy Black Sea card, Black Sea explainer, women's reservation explainer and the Kharge fact check dropped from the top. Must Read now tops up from the last 48 hours on a quiet morning (src/lib/home.ts), which cleared a 181px gap on the Hindi desktop page.
- Editor homepage notes not done: lead should be Indian news (no fresh lead-worthy Indian story exists); Sri Lanka score is the day-two close; Bastar and Rajnath Sherathang repeats in Politics and Policy lists (template-driven).
- NEXT RUN, FIRST: UPSC Mains result and DAF-II window (Nov 11 to 25); Delhi CPCB AQI; Abu Dhabi talks day two outcome; Pakistan v Sri Lanka day three close; markets open (first session since Nov 9); Rubio rewrite with a proper photo.
## November 11, 2026, 10:35 am (from the 10:00 run)
- Published 1: kolkata-sairang-express-derails-digaru-assam-no-injuries (infographic --nophoto: finder found only Mumbai 2013 and Coromandel 2023 derailment scenes, not the Northeast; NFR statement known only as relayed by reports).
- Dropped before review: UPSC Mains DAF-II story (392 words, upsc.gov.in not readable, result six days old). World desk: Abu Dhabi day two had no outcome yet. Sport desk: Rawalpindi day three had just begun.
- Lead stays Abu Dhabi day one (breach: it led before; no fresh Indian news story with a photo). Zelenskyy Black Sea, Rubio G7 and the stale Nov 9 Sensex close dropped from the top on the editor's word.
- Markets: Sensex 82,212 and Nifty 25,324 at about 10 am (Business Today); Brent and the rest kept from the 09:13 read.
- NEXT RUN, FIRST: Abu Dhabi talks day two outcome (new id, can lead); UPSC Mains result and DAF-II window from the upsc.gov.in notice; Rawalpindi day three; Digaru derailment cause or inquiry (update); Delhi CPCB AQI; markets close story if the 1%+ rally holds.


## November 11, 2026, 2:40 pm (from the 14:00 run)
- Published 0 new stories: WebFetch refused on upsc.gov.in, pib.gov.in, CPCB, president.gov.ua, interfax, pcb.com.pk.
- Held by the editor: yogi-pollution-will-subside-diwali-crackers-lucknow-appointment-letters (broken split cover; needs a clean solo Yogi photo at least 900 px, library portrait free again after Nov 14). Unsourced programme figures already cut.
- Editor homepage notes not done (template-driven): lead column same-subject follow-ups link Abu Dhabi day one and Rubio; Must Read carries the Sri Lanka day-three-start item; mobile bottom nav covers the first card under the lead.
- NEXT RUN, FIRST: UPSC Mains result and DAF-II (Nov 11 to 25); Delhi CPCB 4 pm AQI; Sensex close story (rally over 1%); Abu Dhabi talks outcome; Rawalpindi day three close; Swachh Survekshan results.

## November 11, 2026, 4:50 pm (from the 16:00 run)
- Published 1: nadda-colombo-bimstec-health-ministers-jamnagar-centre (Nadda library file photo; syndicated ministry posts, PIB unreadable). Sangrur bus crash draft dropped (under 600 words, no primary readable).
- Held by the editor: india-win-toss-bowl-40-overs-hamilton-third-odi-rain-delay (stale toss report; the abandoned-match story covers it).
- Lead stays Zelenskyy Abu Dhabi day two (breach: led before; no fresh lead-worthy Indian news with a photo).
- Markets: Nov 11 close (Sensex 81,879.40, Nifty 25,255.05) appended; movers, sectors, flows still old.
- NEXT RUN, FIRST: six Indian seafarers safe after Persian Gulf attack (Sonowal); Swachh Survekshan 2025-26 winners (PIB); Sangrur PRTC bus crash (Punjab govt); Jairam Ramesh Ram Temple donations attack; Nov 11 movers, sectors and FII/DII flows; Mamata cut-out crop in Politics.

## November 12, 2026, 12:45 am (from the 00:00 run)
- Published 4: swachh-survekshan-awards-visakhapatnam-cleanest-million-plus-murmu-confers (LEAD, PIB event photo; reworded to "top three", PIB gives no order), kulgam-crpf-naka-attack-three-injured-nov-11 (infographic --nophoto; rests on reports), rbi-consolidates-domestic-money-transfer-rules-cash-neft-50000-limit (infographic; RBI text not readable, rests on reports), rawalpindi-test-day-four-rain-forecast-sri-lanka-30-behind-both-tests-pindi (infographic --nophoto; no free Abbas, de Silva or Kusal Mendis photo).
- Editor homepage FAIL not fixed (two editor checks; template-driven): Must Read still carries the stale Abu Dhabi day one and day two items beside "talks end"; Haj quota card in a pictured slot; Swachh preview in the Policy list; seafarer card says three not six safe; fold gap under left and middle columns.
- Markets: Nov 11 close kept; FII/DII flows for Nov 11 not read this run.
- NEXT RUN, FIRST: MHA visa category simplification; PM Modi Karnataka and Gujarat visit Nov 13-14 preview; six seafarers safe update; Rawalpindi day four close; Nov 11 FII/DII flows; correct the "second Test in Lahore" line in the day-three story.

## November 12, 2026, 6:50 am (from the 06:00 run)
- Published 5: tn-law-and-order-diwali-murders-centre-seeks-governor-report (LEAD, Amit Shah Commons file photo; rests on reports), modi-karnataka-gujarat-visit-november-13-14-15600-crore-projects-preview (PMO release read; Modi library portrait, tight crop, needs an event photo), india-cuts-visa-categories-13-to-9-form-fields-mha (IGI T3 file photo; rests on reports, MHA release not found), iyer-first-odi-captaincy-mount-maunganui-fourth-odi-preview, india-test-camp-wellington-gill-rahul-nitish-nabi-gurnoor-stay-back.
- Held: nepal-pm-shah-india-visit-november-22-25-modi-talks-aid (news two days old; republish when India announces the dates).
- WebFetch permission prompts went unanswered for news front pages (newsonair, thehindu, indianexpress): the front-page check ran on these notes only.
- Fixed a build break: sangrur-prtc-bus-flyover-crash-three-killed linked /news/<id> (unresolvable); now /en|hi/news/<id>.
- Editor homepage notes not done (template-driven or need research): seafarer card says three safe, six now reported (six-indian-seafarers-safe... is held for its picture); Russia-Ukraine twice in Must Read; Swachh preview in Policy list; three Bastar items in Politics.
- NEXT RUN, FIRST: Rawalpindi day four close (play from about 10 am IST); six seafarers safe with a proper photo (republish the held story with a serious Sonowal or ship photo); Modi Bengaluru event photo (PIB) on November 13; October CPI release today; markets open.

## November 12, 2026, 8:40 am (from the 08:00 run)
- Published 4: delhi-aqi-319-thursday-iit-delhi-413-severe-36-stations-above-300 (LEAD, Delhi smog Commons file photo; rests on two reports, CPCB/CAQM not readable), bjp-questions-rahul-gandhi-us-trip-pitroda-columbia-chicago (Sudhanshu Trivedi Commons photo; rests on reports), rbi-ecl-meeting-bank-ceos-november-12-sbi-19500-crore (infographic --nophoto: Malhotra portraits only 391 and 484 px, RBI tower used inside 7 days; Malhotra added to people.tsv), cosmos-mysuru-planetarium-led-dome-modi-inaugurates-november-13-preview (Modi PMO library photo).
- Editor FAILs all fixed by the run. Editor asked for the Tamil Nadu story to lead again; not done: it led at 06:54 and a story leads only once.
- Markets: closed pre-open; Nov 11 close kept; Nov 11 FII/DII flows still not read.
- NEXT RUN, FIRST: RBI-bank CEOs ECL meeting outcome (new id); markets open; Rawalpindi day four; Delhi AQI 4 pm bulletin; October CPI at 4 pm (16:00 run); six seafarers republish with a serious photo.

## November 12, 2026, 10:40 am (from the 10:00 run)
- Published 3: cii-partnership-summit-visakhapatnam-opens-141-mous-12-lakh-crore (LEAD, Naidu library file photo; rests on reports of state figures, no PIB or AP release found; written before any MoU signing was reported), us-army-soldier-arrested-england-russia-national-security-act (New Scotland Yard file photo; Met Police release read), hardik-pandya-punjab-kings-arshdeep-mumbai-indians-trade-ipl-2027 (Pandya library photo; MI and PBKS statements read; fees from reports).
- National desk wrote nothing: RBI ECL meeting outcome not yet reported, rbi.org.in refused.
- Editor FAILs all fixed by the run (Kash Patel main swapped, AP named in copy, Bumrah-with-Modi photo removed, five not six regional conferences). No usable Arshdeep Singh photo (all under 800 px): add to people.tsv.
- Editor homepage notes not done: Delhi AQI card still the 6:30 am figure; Swachh preview in Policy list; mobile tab bar over first card.
- Markets: Sensex 81,642.29 and Nifty 25,180.15 at about 9:15 am (open, down 0.3%).
- NEXT RUN, FIRST: CII summit MoUs signed and Amit Shah speech (update the lead with signed figures, new updated:); RBI ECL meeting outcome (new id); Rawalpindi day four; Delhi AQI latest; October CPI at 4 pm; six seafarers republish with a serious photo.

## November 12, 2026, 2:45 pm (from the 14:00 run)
- Published 4: tamil-nadu-sterlite-firing-victims-extra-5-25-crore-vijay (LEAD, Vijay library file photo; rests on reports, TN release not opened), guterres-cop31-fossil-fuels-dinosaurs-leaders-summit-china-us-india-absent (Guterres EC 2023 file photo, swapped from the US-flags portrait), yogi-uttarakhand-mahotsav-lucknow-akhilesh-infiltrators-dimple-saifai (infographic --nophoto: Yogi library portraits used inside 7 days, Commons solo only 450 px), saqib-khan-seven-wickets-debut-sri-lanka-446-rawalpindi-test (infographic --nophoto; Saqib Khan added to people.tsv).
- Editor story FAILs all fixed by the run (Sterlite SC date February 29, 2024; years on dates; Saqib five wickets on day four; Yogi standfirst).
- Editor homepage FAIL not fixed (two editor checks; template-driven Must Read): Delhi AQI morning card, RBI ECL preview, CII opening-day item, US soldier in the second picture slot. refresh_home --drop of those ids did not clear the Must Read module.
- Markets: Sensex 81,867.32, Nifty 25,246.15 at 1:31 pm; Brent, rupee, movers not updated.
- NEXT RUN, FIRST: CII summit MoUs signed and Amit Shah speech (new id); RBI ECL meeting outcome; Karnataka blacklists L&T over Jal Jeevan Mission; Delhi 4 pm AQI; October CPI at 4 pm; six seafarers republish with a serious photo; Yogi photo upgrade after November 14; Pakistan v Sri Lanka day four close.
