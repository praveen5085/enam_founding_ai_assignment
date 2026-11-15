from datetime import datetime,timedelta,timezone
from .network import search

def growth(current,base): return round((current/base-1)*100,2) if base>0 else None

def results(current=(64000,16000,15000,12000),previous=(62000,15000,14000,11000),year=(59000,14000,13000,10000)):
    return [dict(metric=k,actual=c,qoq=growth(c,p),yoy=growth(c,y),unit='INR crore') for k,c,p,y in zip(['Revenue','EBITDA','PBT','PAT'],current,previous,year)]

BIO_SOURCE='Meera Rao joined TCS in 2017 after serving in finance at Infosys. She holds an MBA from IIM Ahmedabad and has led treasury and financial planning teams.'
def biography():
    return dict(summary='Meera Rao is a fictional finance leader with TCS and Infosys experience, an IIM Ahmedabad MBA, and treasury and planning responsibilities.',source_text=BIO_SOURCE,source='Synthetic appointment filing',synthetic=True)

async def enriched_feed(hours=24):
    import os
    from .research import llm,normalized
    data=feed(hours)
    if not os.getenv('OPENAI_API_KEY'): return data
    for item in data['material']:
        if item['category']!='management_change':continue
        try:
            value=await llm(os.getenv('EXTRACTION_MODEL','gpt-4.1-mini'),'Extract source-grounded biography facts. Return JSON {"facts":[{"text":"verbatim fact from source"}]}. Do not invent. Source: '+BIO_SOURCE)
            facts=value['facts']
            if not facts or any(not isinstance(f.get('text'),str) or not f['text'].strip() or normalized(f['text']) not in normalized(BIO_SOURCE) for f in facts): raise ValueError('Unsupported biography facts')
            item['biography']['summary']='Fictional profile: '+' '.join(f['text'] for f in facts)
            item['biography']['enrichment']='model-extracted, source-validated facts'
        except Exception:
            item['biography']['enrichment']='deterministic fallback; original filing preserved'
    return data

def feed(hours=24,now=None):
    now=now or datetime.now(timezone.utc)
    specs=[('TCS','results',1,'Quarterly earnings released'),('Asian Paints','results',3,'Quarterly results and margins'),('TCS','management_change',5,'Meera Rao appointed CFO'),('Reliance','capex',8,'New energy investment approved'),('Sun Pharma','M&A',12,'Specialty portfolio acquisition'),('Infosys','unclassified',20,'Customer partnership update'),('Titan','postal_ballot',35,'Postal ballot notice'),('HDFC Bank','agm_egm',60,'Annual general meeting notice'),('Bharti Airtel','capex',90,'Network capacity expansion'),('Bajaj Finance','unclassified',150,'Investor presentation')]
    material=[];routine=[]
    for i,(company,kind,age,title) in enumerate(specs):
        if age>hours: continue
        item=dict(id=i,company=company,category=kind,title=title,published_at=(now-timedelta(hours=age)).isoformat(),synthetic=True,original_text=f'SYNTHETIC FILING: {company}. {title}. For demonstration only.',priority=1 if kind in ['results','management_change','M&A','capex'] else 2)
        if kind=='results': item['results']=results() if company=='TCS' else results((9000,1800,1600,1200),(8500,1600,1400,1000),(8200,1500,1300,900))
        if kind=='management_change': item.update(biography=biography(),network=search('Meera Rao')['profiles'])
        (routine if kind in ['postal_ballot','agm_egm'] else material).append(item)
    return dict(synthetic=True,material=sorted(material,key=lambda x:(x['priority'],x['published_at'])),routine=routine)
