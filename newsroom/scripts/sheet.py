import json,sys,os
from PIL import Image,ImageDraw,ImageFont
base=sys.argv[1]; out=sys.argv[2]; tag=sys.argv[3]
c=json.load(open(sys.argv[4] if len(sys.argv)>4 else f'{base}/photo-candidates/candidates.json'))
J={}
used=set(str(p['sourceUrl']).split('/')[-1] for p in json.load(open('/home/claude/gandhinews/content/photos.json')))
keys=[k for k in c if c[k]['candidates']]
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
per=10
for si in range(0,len(keys),per):
    ks=keys[si:si+per]; W=5*250+10; H=len(ks)*215
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    for r,k in enumerate(ks):
        y=r*215; d.text((5,y+2),f"{k} {J.get(k,{}).get('article','')[:60]} | {c[k]['query']}",fill='black',font=F)
        for cd in c[k]['candidates']:
            try: t=Image.open(f"{base}/photo-candidates/thumbs/{cd['thumb']}").convert('RGB')
            except: continue
            t.thumbnail((240,180)); x=5+cd['n']*250; im.paste(t,(x,y+22))
            u=cd['url'].split('/')[-1]
            d.text((x,y+22),str(cd['n'])+(' USED' if u in used else ''),fill='red',font=F)
    im.save(f'{out}/{tag}{si//per}.jpg',quality=80)
    print(f'{out}/{tag}{si//per}.jpg')
