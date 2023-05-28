from datetime import datetime, timedelta
import os,sys,html2text,cv2
import urllib.parse
import html,re,time,json
import markdown
import rg
from bs4 import BeautifulSoup as bs
from bs4 import Comment
import xmltodict

n=0

def english2date(a):
    d=re.findall('\d+',a)
    y=d[1]
    dd=d[0]
    mo=a.split(' ')[1]
    m=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    for b in range(len(m)):
        if mo==m[b]:
            mo=b+1
    return'-'.join([y,str(mo).rjust(2).replace(' ','0'),dd.rjust(2).replace(' ','0')])

l='https://cn.nytimes.com/rss/'
l2='https://cn.nytimes.com'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
if not os.path.exists('index.list'):
    h=rg.rget(l).text
    hl=xmltodict.parse(h)
    f=open('index.json','w+');f.write(json.dumps(hl));f.close()
else:
    f=open('index.json','r');hl=json.loads(f.read());f.close()
#title,source,description,time,text,type,images,publisher,creator,publisher,category
lmt={'title':'title','source':'link','description':'description','time':'pubDate','creator':'dc:creator','category':'category'}
nhl=[]
for b in hl['rss']['channel']['item']:
    i={}
    for a in lmt.keys():
        i[a]=b[lmt[a]]
        if a=='source':
            i[a]=i[a].split('?')[0]
        if a=='time':
            i[a]=i[a].split(', ')[1]
            d2=' '.join(i[a].split(' ')[:3])
            t=i[a].split(' ')[3]
            z=i[a].split(' ')[-1]
            d2=english2date(d2)
            i[a]='%sT%s%s:%s'%(d2,t,z[:3],z[-2:])
        if a=='description':
            i[a]=bs(i[a],'html.parser').get_text()
    nhl.append(i)

hl=nhl
hl.sort(key=lambda x:x['time'],reverse=True)

print('\n'.join([repr(a)for a in hl]))

if not os.path.exists('JSON-src'):os.mkdir('JSON-src')
dr=os.listdir('JSON-src')
if len(dr)==0:
    nn=0
    ed=''
    for a in range(len(hl)):
        i=hl[a]
        t=rg.rget(i['source']).text
        s=bs(t,'html.parser')
        ms=[['og:type','type'],['article:publisher','publisher']]
        i0={b[1]:s.find('meta',{'property':b[0]}).get('content')for b in ms}
        i.update(i0)

        im0=str(s.find('figure',{'class':'article-span-photo'}).find('img'))
        tt=str(s.find('section',{'class':'article-body'}))
        ta='%s\n%s'%(im0,tt)

        s=bs(ta,'html.parser')

        for x in s.find_all('div',{'class':'article-paragraph'}):
            n=s.new_tag('p')
            n.contents=x.contents
            x.replace_with(n)

        invalid_tags=['div','section','figure']
        for tag in invalid_tags:
            for match in s.findAll(tag):
                match.replaceWithChildren()
        s.prettify()

        i['text']=str(s)

        ls={'a':'href','img':'src'}
        s=bs(i['text'],'html.parser')
        for c in ls.keys():
            ss=s.find_all(c)
            for b in ss:
                v=b.find_all()
                co=b.contents.copy()
                n=s.new_tag(c)
                u=b.get(ls[c])
                if not u:continue
                n[ls[c]]='%s%s'%(l2,u)if(u[0]in['/','.'])and('http'not in u)else u
                n.extend(v)
                n.contents=co
                b.replace_with(n)

        for x in s.find_all('small'):
            if x.get_text()=='广告':
                x.decompose()

        rmt=['h1']
        for z in rmt:
            for x in s.findAll(z):
                n=s.new_tag('h2')
                n.string=x.string
                x.replace_with(n)

        im=[b.get('src').split('?')[0].replace('\n','')for b in s.find_all('img')]
        nim=[]
        for b in im:
            if b not in nim:nim.append(b)
        i['images']=nim
        i['text']=re.sub('\\n{2,}','\\n',str(s.prettify()).strip())
        dd=i['time']
        if dd<d:break
        for z in i.keys():
            i[z]=i[z].strip()if isinstance(i[z],str)else i[z]
        if not os.path.exists(pa:='JSON-src/%s.json'%i['time']):
            print(i)
            f=open(pa,'w+');f.write(json.dumps(i));f.close()
        else:
            if'up'in locals():
                if i['text']!=up:
                    while True:
                        nn+=1
                        i['time']='%sT%s:%s'%(i['time'].split('T')[0],
                                                      str(int(i['time'].split('T')[1].split(':')[0])-nn),
                                                      ':'.join(i['time'].split('T')[1].split(':')[1:]))
                        if not os.path.exists(pa:='JSON-src/%s.json'%i['time']):
                            break
                    print(h)
                    f=open(pa,'w+');f.write(json.dumps(i));f.close()
                else:print(i['time'],'已经完成下载。')
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
        imgs.append([h['time'].replace(':','-').replace('+','-'),h['images']])
for a in imgs:
    for z in a[1]:
        if not os.path.exists(pa:='Images/%s/%s'%(a[0],urllib.parse.unquote(z).split('/')[-1].split('?')[0])):
            if not os.path.exists(pa2:='/'.join(pa.split('/')[:-1])):
                os.makedirs(pa2)
            try:im=rg.rget(z,st=True).content
            except:continue
            f=open(pa,'wb+');f.write(im);f.close()
            print(pa,'下载完毕。')
        else:print(pa,'已经完成下载。')
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
        for c in ss:
            n=s.new_tag('img')
            u=c.get('src')
            n['src']=u.replace('\n','').replace('/'.join(u.replace('\n','').split('/')[:-1]),('../Images/%s'%h['time'].replace(':','-').replace('+','-')if'.webp'not in u else'../ConvertedIMGs/%s'%h['time'].replace(':','-').replace('+','-')).split('?')[0]).replace('.webp','.png').split('?')[0]
            c.replace_with(n)
        t=re.sub('\\n{2,}','\\n',str(s.prettify()))
        t=hp.handle(t)
        t='\n\n'.join([z.replace('\n','').strip()for z in t.split('\n\n')if z])
        #title,source,description,time,text,type,images,publisher,creator,publisher,category
        t='''# %s

Creator: %s

Publisher: %s

Published Time: %s

Description: %s

Images: %s

Category: %s

Type: %s

<!--METADATA-->

%s

Source: %s'''%('%s...'%u[:96-3]if len(u:=h['title'])>96 else u,
               h['creator'],
               h['publisher'],
               h['time'],
               h['description'],
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['images']]),
               h['category'],
               h['type'].title(),
               t,
               '[%s](%s)'%(h['source'],h['source']))
        if not os.path.exists(pa1:='MDs/%s.md'%b.split('.json')[0]):
            f=open(pa1,'w+');f.write(t);f.close()
            print(h['time'],'转换为MD完毕。')
        else:print(h['time'],'已经转换为MD。')
        if not os.path.exists(pa:='HTMs/%s.htm'%b.split('.json')[0]):
            f=open(pa,'w+');f.write(markdown.markdown(t));f.close()
            print(h['time'],'转换为HTM完毕。')
        else:print(h['time'],'已经转换为HTM。')
