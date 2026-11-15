from datetime import datetime, timedelta, timezone
import re

NAMES = ['Aarav Shah','Meera Rao','Vikram Sethi','Ananya Iyer','Rohan Mehta','Kavya Menon','Arjun Nair','Neha Kapoor','Dev Patel','Isha Sen','Rahul Jain','Priya Das']
EMPLOYERS = ['ENAM','TCS','Asian Paints','Sun Pharma','Infosys','HDFC Bank','Reliance','Cipla','Bharti Airtel','Larsen & Toubro','Titan','Bajaj Finance']
SECTORS = ['Investing','IT','Consumer','Pharma','IT','Banking','Energy','Pharma','Telecom','Industrials','Consumer','Finance']
PROFILES = [dict(id=i+1,name=n,role=['Investment Partner','CFO','Strategy Director'][i%3],employer=EMPLOYERS[i],past_employers=[EMPLOYERS[(i+3)%12]],education=['IIM Ahmedabad','IIT Bombay','ISB'][i%3],sector=SECTORS[i],strength=round(.9-i*.04,2),synthetic=True) for i,n in enumerate(NAMES)]
EDGES = [(0,1),(0,4),(0,6),(0,9),(1,2),(1,3),(4,5),(4,7),(6,8),(9,10),(9,11),(6,12)]

def path_to(pid):
    direct = {b for a,b in EDGES if a == 0}
    if pid in direct: return ['You', PROFILES[pid-1]['name']]
    for a,b in EDGES:
        if a in direct and b == pid: return ['You', PROFILES[a-1]['name'],PROFILES[pid-1]['name']]
    return None

def search(q, now=None, events=None):
    now = now or datetime.now(timezone.utc)
    tokens = [t for t in re.findall(r'[a-z0-9]+',q.lower()) if t not in {'or','and','to','an','a','the','second','degree','paths','executive','reconnect'}]
    results=[]
    for p in PROFILES:
        reasons=[]; score=0
        for field,weight in [('name',8),('employer',5),('past_employers',4),('education',3),('sector',3),('role',2)]:
            value=str(p[field]).lower()
            if any(t in value for t in tokens): reasons.append(field.replace('_',' ')); score+=weight
        if not tokens or score:
            path=path_to(p['id'])
            results.append({**p,'score':score,'reasons':reasons,'path':path,'relationship':'proven synthetic graph' if path else 'contextual overlap','identity_candidate':'name' in reasons})
    prompts=[]
    for e in events or []:
        when=datetime.fromisoformat(e['published_at'])
        if now-timedelta(hours=24) <= when <= now:
            for p in PROFILES:
                if e['company'] in [p['employer'],*p['past_employers']]: prompts.append(dict(person=p['name'],reason=f"Reconnect about {e['company']}: {e['title']}",path=path_to(p['id'])))
    return dict(synthetic=True,profiles=sorted(results,key=lambda p:-p['score']),edges=EDGES,reconnect=prompts)
