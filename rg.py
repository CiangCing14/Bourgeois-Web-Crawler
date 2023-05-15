import requests as r
import time

he={'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0'}

def rget_cycle(a,to,st,rn):
    rn+=1
    if rn>5:
        print(a)
        raise RuntimeError
    time.sleep(1)
    return rget(a,to,st,rn)

def rget(a,to=10,st=False,rn=0):
    try:return r.get(a,headers=he,timeout=to,stream=st)
    except:return rget_cycle(a,to,st,rn)

def rpost_cycle(a,d,to,st,rn):
    rn+=1
    if rn>5:
        raise RuntimeError
    time.sleep(1)
    return rpost(a,d,to,st,rn)

def rpost(a,d,to=10,st=False,rn=0):
    try:return r.post(a,headers=he,data=d,timeout=to,stream=st)
    except:return rpost_cycle(a,d,to,st,rn)

def valid_cycle(a,te,to,st,rn):
    rn+=1
    if rn>5:
        raise RuntimeError
    time.sleep(1)
    return valid(a,te,to,st,rn)

def valid(a,te,to=10,st=False,rn=0):
    ret=rget(a,to,st)
    return valid_cycle(a,te,to,st,rn)if te not in ret.text else ret

def revideo(a):
    if not'<video'in a:return a
    b=a.split('<video')
    b0=b[0]
    b1=b[1:]
    b2=[]
    for c in b1:
        c=[c.split('src=')[1].split('"')[0].split('\'')[0][1:],c.split('</video>')[1]]
        c[0]='<p>请查看影片链接：<a href="%s">%s</a></p>'%(c[0],c[0])
        c=''.join(c)
        b2.append(c)
    b1=''.join(b2)
    r='%s%s'%(b0,b1)
    return r
