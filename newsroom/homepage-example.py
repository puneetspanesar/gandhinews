import json,os
p='content/homepage.json';h=json.load(open(p))
def ex(s):
    return any(os.path.exists(f'content/en/{t}/{s}.md') for t in ['news','explainer','editorial','factcheck','tracker','topic'])
h['lead']={"id":"cjp-lehra-do-tiranga-dipke-neha-bora-detained-connaught-place","chart":1,
 "overlay":{"kicker":{"en":"Connaught Place, Friday evening","hi":"कनॉट प्लेस, शुक्रवार शाम"},
  "value":{"en":"150 held, Central Park locked","hi":"150 हिरासत में, सेंट्रल पार्क पर ताला"},"text":{"en":"","hi":""}},
 "dataBox":[
  {"icon":"users-three","color":"#cc0000","value":{"en":"~150","hi":"करीब 150"},"label":{"en":"people detained in central Delhi","hi":"लोग मध्य दिल्ली में हिरासत में"}},
  {"icon":"clock","color":"#8f0000","value":{"en":"5 pm","hi":"शाम 5 बजे"},"label":{"en":"Dipke held minutes before the start","hi":"शुरू होने से कुछ मिनट पहले डिपके हिरासत में"}},
  {"icon":"megaphone","color":"#0d0d0d","value":{"en":"Mandi House","hi":"मंडी हाउस"},"label":{"en":"where Neha Bora was detained","hi":"जहाँ नेहा बोरा को हिरासत में लिया गया"}},
  {"icon":"scales","color":"#6e6e6e","value":{"en":"Sec 163","hi":"धारा 163"},"label":{"en":"BNSS orders used to bar the gathering","hi":"बीएनएसएस आदेश, जिनसे सभा रोकी गई"}}],
 "relatedBelow":["dipke-detention-undeclared-emergency-mamata-rajnath-anarchy","supreme-court-traders-plea-central-park-shutdown-cjp"],
 "relatedBeside":["supreme-court-contempt-notice-sanjay-raut-nikhil-wagle","sensex-nifty-it-rally-weekly-gain-october-16","zelenskyy-asks-eu-70-billion-trump-disgrace-row","saudi-houthi-war-crimes-us-tightens-iran-sanctions","gill-iyer-split-odi-captaincy-new-zealand-bumrah-jadeja-out"]}
B=lambda l,le,lh,te,th:{"link":l,"lead":{"en":le,"hi":lh},"text":{"en":te,"hi":th}}
h['briefing']['items']=[
 B("cjp-lehra-do-tiranga-dipke-neha-bora-detained-connaught-place","Delhi:","दिल्ली:","Dipke, Neha Bora and about 150 others detained at the CJP flag protest.","सीजेपी के तिरंगा प्रदर्शन में डिपके, नेहा बोरा समेत करीब 150 लोग हिरासत में।"),
 B("dipke-detention-undeclared-emergency-mamata-rajnath-anarchy","Reaction:","प्रतिक्रिया:","Mamata calls it an 'undeclared Emergency'; Rajnath blames the opposition.","ममता ने इसे \"अघोषित आपातकाल\" कहा; राजनाथ ने विपक्ष पर निशाना साधा।"),
 B("supreme-court-contempt-notice-sanjay-raut-nikhil-wagle","Supreme Court:","सुप्रीम कोर्ट:","contempt notice to Sanjay Raut and Nikhil Wagle.","संजय राउत और निखिल वागले को अवमानना नोटिस।"),
 B("sensex-nifty-it-rally-weekly-gain-october-16","Markets:","बाज़ार:","IT shares lift the Sensex 414 points; up 3.1% for the week.","आईटी शेयरों से सेंसेक्स 414 अंक चढ़ा; हफ़्ते में 3.1% बढ़त।"),
 B("mann-phillaur-punjab-defamed-drugs-mha-seeks-reports","Punjab:","पंजाब:","Mann says the state is 'defamed' over drugs; Centre seeks reports.","मान बोले, नशे पर पंजाब को बदनाम किया गया; केंद्र ने रिपोर्ट मांगी।"),
 B("gill-iyer-split-odi-captaincy-new-zealand-bumrah-jadeja-out","Cricket:","क्रिकेट:","Gill and Iyer split the ODI captaincy for New Zealand; no Bumrah.","न्यूज़ीलैंड दौरे पर गिल और अय्यर में बंटी वनडे कप्तानी; बुमराह नहीं।"),
 B("zelenskyy-asks-eu-70-billion-trump-disgrace-row","Ukraine:","यूक्रेन:","Zelenskyy asks the EU for €70 billion more for 2027.","ज़ेलेंस्की ने 2027 के लिए ईयू से 70 अरब यूरो और मांगे।"),
 B("saudi-houthi-war-crimes-us-tightens-iran-sanctions","Gulf:","खाड़ी:","Saudi Arabia calls Houthi airport strikes war crimes.","सऊदी अरब ने हूती हमलों को युद्ध अपराध बताया।")]
h['topStories']={"big":{"id":"supreme-court-yes-bank-at1-judgment-rbi-bystander","also":["yes-bank-q2-results-preview-at1-verdict","at1-bonds-explained-yes-bank-supreme-court-ruling"]},
 "list":["delhi-sir-reverification-47-lakh-deleted-voters","ec-hearing-trinamool-ownership-dispute-october-30","supreme-court-to-hear-plea-rahul-gandhi-pushed-pregnant-journalist","prashant-kishor-samrat-choudhary-lord-ram-remark-arrogance","pinarayi-vijayan-supreme-court-cmrl-fir-vacation-listing"]}
h['startHere']=["eu-russia-sanctions-indian-firms-explained","asian-para-games-classification-explained","bonus-issue-explained-tech-mahindra","at1-bonds-explained-yes-bank-supreme-court-ruling","whos-who-uttar-pradesh-2027-contest","daily-crr-rule-explained-banks-borrowers"]
h['opinion']=["protest-needs-more-than-one-designated-site","after-yes-bank-ruling-rbi-must-own-investor-protection"]+[x for x in h['opinion'] if x not in("protest-needs-more-than-one-designated-site","after-yes-bank-ruling-rbi-must-own-investor-protection")][:3]
S={s['section']:s for s in h['sections']}
S['politics']['list']=["jk-ias-officer-abuses-jkas-officer-omar-abdullah-protection","delhi-high-court-refuses-stay-sc-st-fir-woman-journalist-acp","zubeen-garg-cousin-sandipan-bail-gauhati-high-court"]
S['economy']['lead']="rupee-sixth-gain-forex-reserves-fall-726-billion"
S['economy']['list']=["india-current-account-deficit-august-5-2-billion","flipkart-group-fy26-revenue-1-45-lakh-crore-loss-narrows","cult-fit-sebi-nod-ipo-950-crore-fresh-issue","pnb-federal-bank-q2-profit-record"]
S['states']['lead']="mann-phillaur-punjab-defamed-drugs-mha-seeks-reports"
S['states']['list']=["andhra-local-body-nominations-violence-punganur-mithun-reddy","manipur-kamjong-ambush-kuki-woman-killed-couple-missing","delhi-rain-clears-air-aqi-86-satisfactory"]
S['policy']['lead']="jaishankar-rubio-talks-mumbai-october-20-mea"
S['policy']['list']=["ins-samarthak-commissioning-karwar","mea-rejects-us-congresswoman-remarks-electoral-process","india-mongolia-defence-joint-working-group","pm-setu-1195-crore-five-iti-clusters"]
D={s['section']:s for s in h['desks']}
D['world']['lead']="zelenskyy-asks-eu-70-billion-trump-disgrace-row"
D['world']['list']=["saudi-houthi-war-crimes-us-tightens-iran-sanctions","indonesia-stocks-worst-day-since-1998-msci-downgrade","trump-says-us-in-denuclearisation-talks-russia-china"]
D['science']['lead']="reliance-responds-musk-starlink-never-feared-competition"
D['science']['list']=["cert-in-warns-ai-agents-accessed-indian-systems","anthropic-gives-metr-researchers-employee-level-access","origin-raises-20-million-wall-finishing-construction-robots"]
D['sports']['lead']="gill-iyer-split-odi-captaincy-new-zealand-bumrah-jadeja-out"
D['sports']['list']=["bhuvneshwar-added-india-squad-arshdeep-shoulder-bengaluru","asian-para-games-bhavina-suhas-krishna-nagar-winning-start","komal-u23-worlds-bronze-amruta-pujari-final"]
W=lambda i,de,dh,te,th,l:{"icon":i,"date":{"en":de,"hi":dh},"text":{"en":te,"hi":th},"link":l}
h['weekAhead']=[
 W("trophy","Sat 17 Oct","शनि, 17 अक्टूबर","India v West Indies decider in Bengaluru; Bhuvneshwar in for Arshdeep.","बेंगलुरु में भारत-वेस्टइंडीज़ निर्णायक मैच; अर्शदीप की जगह भुवनेश्वर।","bhuvneshwar-added-india-squad-arshdeep-shoulder-bengaluru"),
 W("bank","Sat 17 Oct","शनि, 17 अक्टूबर","YES Bank results, its first since the AT-1 verdict.","एटी-1 फ़ैसले के बाद यस बैंक के पहले नतीजे।","yes-bank-q2-results-preview-at1-verdict"),
 W("users-three","Sun 18 Oct","रवि, 18 अक्टूबर","Asian Para Games: India's medal events build in Aichi-Nagoya.","एशियाई पैरा खेल: आइची-नागोया में भारत के पदक मुकाबले।","asian-para-games-bhavina-suhas-krishna-nagar-winning-start"),
 W("megaphone","Mon 19 Oct","सोम, 19 अक्टूबर","Jhota action committee plans protests at AAP leaders' homes.","झोटा एक्शन कमेटी का आप नेताओं के घरों के बाहर प्रदर्शन।","mann-phillaur-punjab-defamed-drugs-mha-seeks-reports"),
 W("handshake","Tue 20 Oct","मंगल, 20 अक्टूबर","Jaishankar and Rubio meet in Mumbai; rebel TMC MPs' deadline.","मुंबई में जयशंकर-रुबियो वार्ता; बागी टीएमसी सांसदों की समय-सीमा।","jaishankar-rubio-talks-mumbai-october-20-mea")]
# verify every id
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k in('id','link','lead','article') and isinstance(v,str): yield v
            elif k in('list','also','relatedBelow','relatedBeside') and isinstance(v,list): yield from v
            else: yield from walk(v)
    elif isinstance(o,list):
        for x in o:
            if isinstance(x,str): yield x
            else: yield from walk(x)
bad=[s for s in walk({k:h[k] for k in['lead','briefing','topStories','startHere','opinion','sections','desks','weekAhead']}) if '-' in s and not ex(s)]
print('missing',bad)
json.dump(h,open(p,'w'),ensure_ascii=False,indent=1)
