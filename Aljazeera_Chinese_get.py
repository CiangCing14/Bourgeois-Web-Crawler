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

he='''Host: chinese.aljazeera.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://chinese.aljazeera.net/news/
content-type: application/json
wp-site: chinese
original-domain: chinese.aljazeera.net
Connection: keep-alive
Cookie: _splunk_rum_sid=%7B%22id%22%3A%22f43242c53e3df39c45df5080105173c4%22%2C%22startTime%22%3A1685269221500%7D; _ga_GHMSVDCBRB=GS1.1.1685269222.1.1.1685269379.0.0.0; _ga=GA1.2.730031887.1685269222; AMP_9e2bdeb55f=JTdCJTIyb3B0T3V0JTIyJTNBZmFsc2UlMkMlMjJkZXZpY2VJZCUyMiUzQSUyMjU0NTk2NDE5LTkxNjAtNGY2ZC1iMmQ1LTgzMWVlMTIyZjE5MyUyMiUyQyUyMmxhc3RFdmVudFRpbWUlMjIlM0ExNjg1MjY5Mzc4OTAwJTJDJTIyc2Vzc2lvbklkJTIyJTNBMTY4NTI2OTIyMjYwMCU3RA==; _cb=DGC1akCrsF54BbsnAw; _chartbeat2=.1685269222700.1685269378800.1.BN41ppCSBqhfCt2cNHjOwhTvxYtK.1; OptanonConsent=isGpcEnabled=0&datestamp=Sun+May+28+2023+10%3A23%3A00+GMT%2B0000+(Coordinated+Universal+Time)&version=202209.1.0&isIABGlobal=false&hosts=&consentId=06978715-62df-4a5a-be56-6e90ab965e75&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0007%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&geolocation=JP%3B13&AwaitingReconsent=false; _gcl_au=1.1.351358514.1685269223; __qca=P0-2062297997-1685269224300; AMP_MKTG_9e2bdeb55f=JTdCJTdE; _gid=GA1.2.372382107.1685269231; OptanonAlertBoxClosed=2023-05-28T10:21:05.500Z; _ga_WFKEPR3HG4=GS1.1.1685269271.1.0.1685269271.0.0.0; _cb_svref=null
TE: Trailers'''

head={}

for a in he.split('\n'):
    head[a.split(': ')[0]]=a.split(': ')[1]

l0='https://chinese.aljazeera.net/news/'
l='https://chinese.aljazeera.net/graphql?wp-site=chinese&operationName=ArchipelagoAjeSectionPostsQuery&variables=%7B%22category%22%3A%22news%22%2C%22categoryType%22%3A%22categories%22%2C%22postTypes%22%3A%5B%22blog%22%2C%22episode%22%2C%22opinion%22%2C%22post%22%2C%22video%22%2C%22external-article%22%2C%22gallery%22%2C%22podcast%22%2C%22longform%22%2C%22liveblog%22%5D%2C%22quantity%22%3A10%2C%22offset%22%3A[NUM]4%7D&extensions=%7B%7D'
l2='https://chinese.aljazeera.net'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
hl=[]
if not os.path.exists('000000.list'):
    for a in range(5):
        if a==0:
            h=rg.rget(l0).text
            s=bs(h,'html.parser')
            h=['%s%s'%(l2,b.find('a').get('href'))for b in s.find_all('article')]
        else:
            h=rg.rget(l.replace('[NUM]',str(a)),hea=head).json()
            h=['%s%s'%(l2,b['link'])for b in h['data']['articles']]
        hl.extend(h)
        f=open('%s.list'%(str(a).rjust(6).replace(' ','0')),'w+');f.write(repr(h));f.close()
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
        f=open(a,'r');h=eval(f.read());f.close()
        hl.extend(h)
print('\n'.join([a for a in hl]))

if not os.path.exists('JSON-src'):os.mkdir('JSON-src')
dr=os.listdir('JSON-src')
if len(dr)==0:
    nn=0
    ed=''
    for a in range(len(hl)):
        i={}
        t=rg.rget(hl[a]).text
        #type,publisher,source,topics,keywords,published time,modified time,author,title,description,text,images
        s=bs(t,'html.parser')

        ms=[['og:type','type']]
        i0={b[1]:s.find('meta',{'property':b[0]}).get('content')for b in ms}
        i.update(i0)

        i0={'publisher':'Al Jazeera',
            'source':hl[a]}
        i.update(i0)

        ms=[['topics','topics'],
            ['keywords','keywords'],
            ['publishedDate','published time'],
            ['lastDate','modified time'],
            ['sourceTaxonomy','author'],
            ['pageTitle','title'],
            ['description','description']]
        i0={b[1]:s.find('meta',{'name':b[0]}).get('content')for b in ms}
        i0['topics']=i0['topics'].split(', ')
        i0['keywords']=i0['keywords'].split(', ')
        i.update(i0)
        
        tt0=str(s.find('figure',{'class':'article-featured-image'}))
        tt1=str(s.find('div',{'class':'wysiwyg wysiwyg--all-content css-10ptoor'}))
        if tt1=='None':tt1=str(s.find('div',{'class':'compact-featured-area__content'}))
        tt='%s\n%s'%(tt0,tt1)
        s=bs(tt,'html.parser')

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
                    print(h)
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
        imgs.append([h['published time'].replace(':','-').replace('+','-'),h['images']])
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
            n['src']=u.replace('\n','').replace('/'.join(u.replace('\n','').split('/')[:-1]),('../Images/%s'%h['published time'].replace(':','-').replace('+','-')if'.webp'not in u else'../ConvertedIMGs/%s'%h['published time'].replace(':','-').replace('+','-')).split('?')[0]).replace('.webp','.png').split('?')[0]
            c.replace_with(n)
        t=re.sub('\\n{2,}','\\n',str(s.prettify()))
        t=hp.handle(t)
        t='\n\n'.join([z.replace('\n','').strip()for z in t.split('\n\n')if z])
        #type,publisher,source,topics,keywords,published time,modified time,author,title,description,text,images
        t='''# %s

Author: %s

Publisher: %s

Published Time: %s

Modified Time: %s

Description: %s

Images: %s

Topics: %s

Keywords: %s

Type: %s

<!--METADATA-->

%s

Source: %s'''%('%s...'%u[:96-3]if len(u:=h['title'])>96 else u,
               h['author'],
               h['publisher'],
               h['published time'],
               h['modified time'],
               h['description'],
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['images']]),
               repr(h['topics']),
               repr(h['keywords']),
               h['type'].title(),
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
