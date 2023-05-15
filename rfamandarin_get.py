from datetime import datetime, timedelta
import os,sys,html2text,cv2
import urllib.parse
import html,re,time,json
import markdown
import rg
from bs4 import BeautifulSoup as bs
import base64
from PIL import Image
from io import BytesIO

n=0

l='https://www.rfa.org/mandarin/story_archive?b_start:int='
l2='https://www.rfa.org/'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
hl=[]
if not os.path.exists('000000.list'):
    for a in range(5):
        h=rg.rget('%s%d'%(l,a*15)).text
        s=bs(h,'html.parser')
        c=s.find_all('div',{'class':'sectionteaser archive'})
        th=[]
        for b in c:
            th.append(b.find('a').get('href'))
        hl.extend(th)
        f=open('%s.list'%(str(a).rjust(6).replace(' ','0')),'w+');f.write(json.dumps(th));f.close()
else:
    fl=[]
    for a in os.walk(sys.path[0]):
        for b in a[2]:
            if a[0]==sys.path[0]:
                if b[-4:]=='list':
                    fl.append([int(b[:-5]),'%s/%s'%(a[0],b)])
    fl.sort(key=lambda x:x[0])
    fl=[a[1]for a in fl]
    for a in fl:
        f=open(a,'r');h=json.loads(f.read());f.close()
        hl.extend(h)
print('\n'.join(hl))

if not os.path.exists('JSON-src'):os.mkdir('JSON-src')
dr=os.listdir('JSON-src')
if len(dr)==0:
    nn=0
    ed=''
    for a in range(len(hl)):
        i=hl[a]
        t=rg.rget(i).text
        i={'source':i}
        sr=bs(t,'html.parser')
        s=sr
        mt={'title':'og:title',
            'description':'og:description'}
        i0={x:s.find('meta',{'property':mt[x]}).get('content')for x in mt}
        i0['description']=re.sub('\s+',' ',i0['description'])
        j=json.loads(s.find('script',{'type':'application/ld+json'}).string)
        i1={'type':j['@type'],
           'published time':j['datePublished'],
           'modified time':j['dateModified'],
           'author':j['author'],
           'publisher':{'type':j['publisher'][0]['@type'],'name':j['publisher'][0]['name']}}
        if not i0['description']:del i0['description']
        i.update(i1)
        i.update(i0)

        i['videos']=[]
        vs=[v for v in s.select('video[id*="vjs_video"]')if v.find('video-js')]
        lvs=len(vs)
        ni=0
        for o in vs:
            ni+=1
            nno=s.new_tag('a')
            ur=o.select('video[src*="http"]').find('source').get('src')
            if not ur:continue
            i['videos'].append(ur)
            nno.string='Video-%s-Link：%s'%(str(ni).rjust(len(str(lvs))).replace(' ','0'),ur)
            nno['href']=ur
            o.replace_with(nno)

        i['audios']=[]
        vs=[v for v in s.find_all('div',{'class':'shadowbox storyaudio'})]
        lvs=len(vs)
        ni=0
        for o in vs:
            ni+=1
            nno=s.new_tag('a')
            ur=o.find('audio').get('src')
            if not ur:continue
            i['audios'].append(ur)
            nno.string='Audio-%s-Link：%s'%(str(ni).rjust(len(str(lvs))).replace(' ','0'),ur)
            nno['href']=ur
            o.replace_with(nno)

        ps=[]
        st=s.find('div',{'id':'storypagemaincol'}).contents
        nst=[]
        sta=False
        for z in st:
            if z.find('<')!=-1:
                if z.get('id')=='headerimg':
                    sta=True
                if z.get('id')=='frontsidebar':
                    sta=False
                if sta:
                    nst.append(z)
        nst=[str(z)for z in nst]
        nst=[z for z in nst if(z!=re.search('\s*',z)[0])]
        st=''.join(nst)
        s=bs(st,'html.parser')
        invalid_tags=['div','span']
        for tag in invalid_tags:
            for match in s.findAll(tag):
                match.replaceWithChildren()
        s.prettify()
        i['text']=str(s)

        ll=[]
        for x in i['videos']:
            if x not in ll:
                ll.append(x)
        i['videos']=ll.copy()

        ll=[]
        for x in i['audios']:
            if x not in ll:
                ll.append(x)
        i['audios']=ll.copy()

        ls={'a':'href','img':'src'}
        s=bs(i['text'],'html.parser')
        for c in ls.keys():
            ss=s.find_all(c)
            for b in ss:
                v=b.find_all()
                n=s.new_tag(c)
                u=b.get(ls[c])
                n[ls[c]]=('%s%s'%(l2,u)if(u[0]in['/','.'])and('http'not in u)else u)if u else''
                n.extend(v)
                b.replace_with(n)

        rmt=['h1']
        for z in rmt:
            for x in s.findAll(z):
                n=s.new_tag('h2')
                n.string=x.string
                x.replace_with(n)

        for o in s.select('img[src*="icon-zoom.png"]'):
            o.decompose()

        im=[b.get('src').split('?')[0].replace('\n','')for b in s.find_all('img')]
        nim=[]
        for b in im:
            if b not in nim:nim.append(b)
        i['images']=nim
        i['imagesn']=['%s.png'%str(z).rjust(6).replace(' ','0')for z in range(len(i['images']))]
        i['text']=re.sub('\\n{2,}','\\n',str(s.prettify()).strip())
        dd=i['published time']
        if dd<d:break
        for z in i.keys():
            i[z]=i[z].strip()if isinstance(i[z],str)else i[z]
        if not os.path.exists(pa:='JSON-src/%s.json'%i['published time']):
            print(i)
            f=open(pa,'w+');f.write(json.dumps(i));f.close()
        else:
            if'up'in locals():
                if i['text']!=up:
                    while True:
                        nn+=1
                        i['published time']='%sT%s:%s'%(i['published time'].split('T')[0],
                                                      str(int(i['published time'].split('T')[1].split(':')[0])-nn),
                                                      ':'.join(i['published time'].split('T')[1].split(':')[1:]))
                        if not os.path.exists(pa:='JSON-src/%s.json'%i['published time']):
                            break
                    print(hl)
                    f=open(pa,'w+');f.write(json.dumps(i));f.close()
                else:print(i['published time'],'已经完成下载。')
        nn+=1
        up=i['text']

if not os.path.exists('Images'):os.mkdir('Images')
imgs=[]
for a in os.walk('JSON-src'):
    for b in a[2]:
        f=open('JSON-src/%s'%b,'r')
        hh=f.read()
        print(hh)
        h=json.loads(hh)
        f.close()
        imgs.append([h['published time'].replace(':','-').replace('+','-'),h['images'],h['imagesn']])
for a in imgs:
    n=0
    for z in a[1]:
        if not os.path.exists(pa:='Images/%s/%s'%(a[0],a[2][n])):
            if not os.path.exists(pa2:='/'.join(pa.split('/')[:-1])):
                os.makedirs(pa2)
            if'http'==z[:4]:
                try:im=rg.rget(z,st=True).content
                except:continue
                f=open(pa,'wb+');f.write(im);f.close()
            elif'data:'==z[:5]:
                image_data = base64.b64decode(z.split(',')[1])
                pil_image = Image.open(BytesIO(image_data))
                pil_image.save(pa)
            else:raise TypeError
            print(pa,'下载完毕。')
        else:print(pa,'已经完成下载。')
        n+=1
if not os.path.exists('ConvertedIMGs'):os.mkdir('ConvertedIMGs')
for a in os.walk('Images'):
    for b in a[2]:
        if'.webp'==b[-5:]:
            if not os.path.exists(pa:='%s/%s'%(a[0].replace('Images','ConvertedIMGs'),b.replace('.webp','.png'))):
                if not os.path.exists(pa2:='/'.join(pa.split('/')[:-1])):
                    os.makedirs(pa2)
                im=cv2.imread('%s/%s'%(a[0],b))
                cv2.imwrite(pa,im)
                print(pa,'转换完毕。')
            else:
                print(pa,'已经完成转换。')

hp=html2text.HTML2Text()
if not os.path.exists('MDs'):os.mkdir('MDs')
if not os.path.exists('HTMs'):os.mkdir('HTMs')
for a in os.walk('JSON-src'):
    for b in a[2]:
        t=''
        f=open('%s/%s'%(a[0],b));h=json.loads(f.read());f.close()
        s=bs(h['text'],'html.parser')
        ss=s.find_all('img')
        nn=0
        for c in ss:
            n=s.new_tag('img')
            u='https://none/%s.png'%str(nn).rjust(6).replace(' ','0')
            n['src']=u.replace('\n','').replace('/'.join(u.replace('\n','').split('/')[:-1]),('../Images/%s'%h['published time'].replace(':','-').replace('+','-')if'.webp'not in u else'../ConvertedIMGs/%s'%h['published time'].replace(':','-').replace('+','-')).split('?')[0]).replace('.webp','.png').split('?')[0]
            c.replace_with(n)
            nn+=1
        t=re.sub('\\n{2,}','\\n',str(s.prettify()))
        t=hp.handle(t)
        t='\n\n'.join([z.replace('\n','').strip()for z in t.split('\n\n')if z])
        t='''# %s

Author: %s

Publisher: %s (%s)

Published Time: %s

Modified Time: %s

Description: %s

Videos: %s

Audios: %s

Images: %s

<!--METADATA-->

%s

Source: %s'''%('%s...'%u[:96-3]if len(u:=h['title'])>96 else u,
               u if(u:=h['author'])else'None',
               h['publisher']['name'],h['publisher']['type'],
               h['published time'],
               h['modified time'],
               u if('description'in h)else'None',
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['videos']]),
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['audios']]),
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['imagesn']]),
               t,
               '[%s](%s)'%(h['source'],h['source']))
        if not os.path.exists(pa1:='MDs/%s.md'%b.split('.json')[0]):
            f=open(pa1,'w+');f.write(t);f.close()
            print(h['published time'],'转换为MD完毕。')
        else:print(h['published time'],'已经转换为MD。')
        if not os.path.exists(pa:='HTMs/%s.htm'%b.split('.json')[0]):
            f=open(pa,'w+');f.write(markdown.markdown(t));f.close()
            print(h['published time'],'转换为HTM完毕。')
        else:print(h['published time'],'已经转换为HTM。')
