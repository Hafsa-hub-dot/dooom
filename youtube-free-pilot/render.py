#!/usr/bin/env python3
"""Original calm pearl/pink Arabic Shorts pilot renderer. Free, no images/music."""
import argparse
import json
import subprocess
from pathlib import Path
from datetime import date,datetime
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
FRMONTHS=['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
def font_path(name):
    p=subprocess.run(['fc-match','-f','%{file}',name],capture_output=True,text=True,check=True).stdout.strip()
    if not Path(p).exists(): raise RuntimeError('Font unavailable '+name)
    return p
def font(name,size):return ImageFont.truetype(font_path(name),max(12,int(size)),layout_engine=ImageFont.Layout.RAQM)
def centered_text(draw,xy,text,face,fill,width,spacing=1.4):
    lines=[]
    for part in str(text).split('\n'):
        line=''
        for word in part.split(' '):
            trial=f'{line} {word}'.strip()
            bb=draw.textbbox((0,0),trial,font=face,direction='rtl')
            if line and bb[2]-bb[0]>width: lines.append(line);line=word
            else:line=trial
        lines.append(line)
    lh=face.size*spacing
    y0=xy[1]-lh*(len(lines)-1)/2
    for i,line in enumerate(lines):
        draw.text((xy[0],y0+i*lh),line,anchor='mm',font=face,fill=fill,direction='rtl',language='ar')
def rgbmix(a,b,t): return tuple(int(a[k]*(1-t)+b[k]*t) for k in range(3))
def create_frame(path,scene_idx,item,cfg,today):
    w,h=cfg['width'],cfg['height'];scale=w/720
    img=Image.new('RGB',(w,h),'#FAF7F3');d=ImageDraw.Draw(img)
    top,bot=(250,247,244),(237,225,221)
    for y in range(h):d.line((0,y,w,y),fill=rgbmix(top,bot,(y/h)**0.85))
    burg=(115,47,66);gold=(182,145,109)
    for i in range(4):
        m=int((55+i*16)*scale)
        d.arc((-int(210*scale)+m,-int(120*scale)+m,int(460*scale)+m,int(550*scale)+m),185,350,fill=(215,192,179),width=max(1,int(2*scale)))
    d.ellipse((int(510*scale),int(980*scale),int(1050*scale),int(1570*scale)),outline=(224,205,194),width=max(1,int(3*scale)))
    d.rounded_rectangle((int(66*scale),int(235*scale),int(72*scale),int(1100*scale)),radius=3,fill=(200,167,151))
    card=(int(92*scale),int(305*scale),int(654*scale),int(915*scale))
    d.rounded_rectangle(tuple(v+int(12*scale) for v in card),radius=int(34*scale),fill=(228,211,207))
    d.rounded_rectangle(card,radius=int(34*scale),fill=(255,253,251),outline=(222,203,198),width=max(1,int(2*scale)))
    label=font('Noto Kufi Arabic:style=Bold',int(26*scale));tit=font('Noto Kufi Arabic:style=Bold',int(37*scale))
    body=font('Noto Naskh Arabic:style=Bold',int(54*scale));hint=font('Noto Naskh Arabic:style=Regular',int(28*scale))
    latin=font('DejaVu Serif:style=Italic',int(26*scale));small=font('DejaVu Sans',int(18*scale))
    d.rounded_rectangle((int(254*scale),int(92*scale),int(550*scale),int(146*scale)),radius=int(22*scale),fill=burg)
    centered_text(d,(402*scale,118*scale),cfg['channel_label'],label,(255,250,245),260*scale)
    d.text((w//2,int(205*scale)),f'✦  {item["id"]}  ✦',anchor='mm',font=small,fill=burg)
    labels=['السؤال','فكّري قليلًا','التفسير','النتيجة']
    contents=[item['hook'],item['bridge'],item['fact'],item['end']]
    centered_text(d,(w/2,393*scale),labels[scene_idx],tit,burg,500*scale)
    d.line((int(230*scale),int(452*scale),int(514*scale),int(452*scale)),fill=gold,width=max(1,int(2*scale)))
    centered_text(d,(w/2,615*scale),contents[scene_idx],body,(58,44,49),480*scale,spacing=1.7)
    centered_text(d,(w/2,833*scale),('الإجابة بعد لحظات' if scene_idx==0 else 'العلم أقرب مما نظن'),hint,(132,105,102),490*scale)
    d.text((w//2,int(1060*scale)),cfg['signature'],anchor='mm',font=latin,fill=burg)
    d.text((w//2,int(1110*scale)),f'{today.day} {FRMONTHS[today.month-1]} {today.year}',anchor='mm',font=small,fill=(131,101,99))
    d.text((w//2,int(1193*scale)),'♡  Subscribe   ·   Share  ♡',anchor='mm',font=small,fill=burg)
    d.line((int(245*scale),int(1150*scale),int(475*scale),int(1150*scale)),fill=gold,width=max(1,int(2*scale)))
    img.save(path,optimize=True)
def select_item(bank,cfg,today):
    offset=(today-date.fromisoformat(cfg['start_date'])).days
    if not 0<=offset<len(bank):raise ValueError(f'CONTENT_BANK_EXHAUSTED: day={offset}, available={len(bank)}. Add new unique stories.')
    return bank[offset]
def render(today):
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf8'))
    bank=json.loads((ROOT/'content_bank.json').read_text(encoding='utf8'))
    item=select_item(bank,cfg,today)
    out=ROOT/'output'/f'{item["id"]}.mp4'
    out.parent.mkdir(parents=True,exist_ok=True)
    frames=ROOT/'frames';frames.mkdir(parents=True,exist_ok=True)
    imgs=[]
    for i in range(4):
        p=frames/f'{item["id"]}_{i+1:02d}.png'
        create_frame(p,i,item,cfg,today);imgs.append(p)
    fps=cfg['fps'];sec=cfg['seconds_per_scene'];trans=cfg['transition_seconds'];w=cfg['width'];h=cfg['height']
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']
    for p in imgs:cmd+=['-loop','1','-framerate',str(fps),'-t',str(sec),'-i',str(p)]
    flt=[]
    for i in range(4):
        flt.append(f"[{i}:v]zoompan=z='min(zoom+0.00018,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps={fps},trim=duration={sec},settb=AVTB,setsar=1,format=yuv420p[z{i}]")
    prev='z0'
    for i in range(1,4):
        key=f'm{i}'
        flt.append(f'[{prev}][z{i}]xfade=transition=fade:duration={trans}:offset={(sec-trans)*i:.3f}[{key}]')
        prev=key
    cmd+=['-filter_complex',';'.join(flt),'-map',f'[{prev}]','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-r',str(fps),'-movflags','+faststart',str(out)]
    subprocess.run(cmd,check=True)
    meta={'video_path':str(out),'date':today.isoformat(),'id':item['id'],'title':item['title'],
        'description':item['caption']+'\n\n'+' '.join(cfg['hashtags']),'tags':item['tags'],
        'made_for_kids':cfg['made_for_kids'],'category_id':cfg['category_id'],'visibility':'private'}
    out.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'ok':True,'video':str(out),'bytes':out.stat().st_size},ensure_ascii=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--date');args=ap.parse_args()
    cfg=json.loads((ROOT/'config.json').read_text(encoding='utf8'))
    today=date.fromisoformat(args.date) if args.date else datetime.now(ZoneInfo(cfg['timezone'])).date()
    render(today)
