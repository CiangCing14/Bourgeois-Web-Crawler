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

l='https://rss.dw.com/rdf/rss-chi-all'
l2='https://www.dw.com/zh'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
if not os.path.exists('index.list'):
    h=rg.rget(l).text
    hl=xmltodict.parse(h)
    f=open('index.json','w+');f.write(json.dumps(hl));f.close()
else:
    f=open('index.json','r');hl=json.loads(f.read());f.close()
#title,source,description,time,subject,id,subjects,keywords,text,videos,images,publisher,author
lmt={'title':'title','source':'link','description':'description','time':'dc:date','subject':'dc:subject','id':'dwsyn:contentID','language':'dc:language'}
hl=[{a:b[lmt[a]]for a in lmt.keys()}for b in hl['rdf:RDF']['item']]

print('\n'.join([repr(a)for a in hl]))

if not os.path.exists('JSON-src'):os.mkdir('JSON-src')
dr=os.listdir('JSON-src')
if len(dr)==0:
    nn=0
    ed=''
    for a in range(len(hl)):
        i=hl[a]
        t=rg.rget(i['source']).text
        sr=bs(t,'html.parser')
        s=sr.find('div',{'class':'col3'})
        mt=['publisher','author']
        i0={x:s.find('meta',{'name':x})for x in mt}
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
        comment=s.find(text=lambda text:isinstance(text,Comment)and'detail_toolbox'in text)
        tools={'subjects':1,
               'keywords':2}
        for e in tools.keys():
            dd=comment.find_next('div')
            while True:
                if dd.find('ul',{'class':'smallList'}):break
                dd=dd.find_next('div')
            dd=dd.find_all('li')
            i[e]=[d.string for d in dd[tools[e]].find_all('a')]
        ps=[]
        st=[z for z in s.find('div',{'class':'longText'}).contents if z]
        nst=[]
        st=[str(z)for z in st]
        for z in st:
            if z.find('年德國之聲版權聲明')!=-1:
                break
            if z.find('年德国之声版权声明')!=-1:
                break
            nst.append(z)
        nst=[z for z in nst if(z!=re.search('\s*',z)[0])]
        st=''.join(nst)
        si=s.find('div',{'class':'picBox full'})
        if si:
            sa=si.find('a')
            sa['href']=sa['link']
            del sa['link'],sa['class'],sa['rel'],sa['style']
            sn=''.join([str(si),st])
        s=bs(sn,'html.parser')if si else s
        invalid_tags=['div']
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

        ls={'a':'href','img':'src'}
        s=bs(i['text'],'html.parser')
        for c in ls.keys():
            ss=s.find_all(c)
            for b in ss:
                v=b.find_all()
                n=s.new_tag(c)
                u=b.get(ls[c])
                n[ls[c]]='%s%s'%(l2,u)if(u[0]in['/','.'])and('http'not in u)else u
                n.extend(v)
                b.replace_with(n)

        for x in s.find_all('div',{'class':'col1'}):
            x.decompose()

        rmt=['h1']
        for z in rmt:
            for x in s.findAll(z):
                n=s.new_tag('h2')
                n.string=x.string
                x.replace_with(n)

        for z in s.find_all('p'):
            if'年德国之声版权声明'in z:z.decompose()

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
        #title,source,description,time,subject,id,subjects,keywords,text,videos,images,publisher,author
        t='''# %s

Author: %s (Language: %s)

Publisher: %s

Time: %s

Description: %s

Videos: %s

Images: %s

Subject: %s

Subjects: %s

Keywords: %s

ID: %s

<!--METADATA-->

%s

Source: %s'''%('%s...'%u[:96-3]if len(u:=h['title'])>96 else u,
               h['author'],
               h['language'],
               h['publisher'],
               h['time'],
               h['description'],
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['videos']]),
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['images']]),
               h['subject'],
               repr(h['subjects']),
               repr(h['keywords']),
               h['id'],
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
