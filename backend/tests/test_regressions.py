import asyncio
from datetime import datetime,timedelta,timezone
from decimal import Decimal
from unittest.mock import AsyncMock
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import research as r,market
from backend.feed import feed,growth,biography,BIO_SOURCE
from backend.network import search

def test_feed_results_and_bio():
    f=feed(168);assert len(f['material'])+len(f['routine'])==10
    cards=[x for x in f['material'] if 'results' in x]
    assert len(cards)==2
    for c in cards: assert [x['metric'] for x in c['results']]==['Revenue','EBITDA','PBT','PAT']
    assert growth(110,100)==10 and growth(10,0) is None and growth(10,-5) is None
    bio=biography();assert bio['summary'] not in BIO_SOURCE
    assert all(s in bio['summary'] for s in ['TCS','Infosys','IIM Ahmedabad'])

def test_rolling_utc_former_employer():
    now=datetime(2026,1,2,0,10,tzinfo=timezone.utc)
    events=[dict(company='Sun Pharma',title='Results',published_at=(now-timedelta(hours=h)).isoformat()) for h in [1,23,25]]
    prompts=search('Pharma or IT',now,events)['reconnect']
    assert len([p for p in prompts if p['person']=='Aarav Shah'])==2
    assert {'IT','Pharma'} <= {p['sector'] for p in search('Pharma or IT')['profiles']}
    assert len(search('Meera Rao')['profiles'][0]['path'])==3

def test_normalized_quotes_reversed_labels_and_rounding():
    docs,data=r.fixtures('TCS');data.quarters[0].quarter='FY2025 Q2'
    data.quarters[0].tone_quote='  TONE:   CAUTIOUSLY OPTIMISTIC. '
    data.quarters[0].metrics['Revenue'].quote='REVENUE   ACTUAL INR CRORE 1020.'
    rows=r.validate(data,docs);assert len(rows)==4
    data.quarters[0].metrics['Revenue'].actual=Decimal('999')
    with pytest.raises(ValueError):r.validate(data,docs)

@pytest.mark.asyncio
async def test_active_key_schema_and_provider_fallback(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-key-not-real')
    docs,_=r.fixtures('TCS')
    monkeypatch.setattr(r,'discover',AsyncMock(return_value=docs))
    monkeypatch.setattr(r,'llm',AsyncMock(return_value={'unexpected':'schema'}))
    result=await r.research('TCS');assert result['synthetic'] and len(result['quarters'])==4
    with pytest.raises(ValueError):await r.research('TCS',False)
    monkeypatch.setattr(r,'discover',AsyncMock(side_effect=RuntimeError('provider down')))
    assert (await r.research('ANYNSE'))['synthetic']

@pytest.mark.asyncio
async def test_synthesis_failure_keeps_live(monkeypatch):
    docs,data=r.fixtures('TCS')
    monkeypatch.setattr(r,'discover',AsyncMock(return_value=docs))
    monkeypatch.setattr(r,'extract',AsyncMock(return_value=data))
    monkeypatch.setattr(r,'llm',AsyncMock(side_effect=RuntimeError('synthesis down')))
    result=await r.research('TCS',False)
    assert not result['synthetic'] and result['narrative_state']=='unavailable'
    assert result['quarters'][0]['metrics']['Revenue']['status']=='within guidance'

@pytest.mark.asyncio
async def test_no_guidance_and_no_key(monkeypatch):
    docs,data=r.fixtures('TCS')
    for q in data.quarters:
        for m in q.metrics.values():m.guidance_low=m.guidance_high=None
    monkeypatch.setattr(r,'discover',AsyncMock(return_value=docs))
    monkeypatch.setattr(r,'extract',AsyncMock(return_value=data))
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    assert (await r.research('TCS'))['synthetic']
    with pytest.raises(ValueError):await r.research('TCS',False)

@pytest.mark.asyncio
async def test_batched_retry_and_completed_session(monkeypatch):
    market.CACHE.clear();calls=[]
    index=pd.date_range(end='2026-01-19',periods=14,freq='B')
    good=pd.DataFrame({'Close':[100]*13+[105],'Volume':[100]*13+[300]},index=index)
    def download(**kwargs):
        calls.append(kwargs['tickers'])
        return pd.concat({s:(good if len(calls)>1 or s!='TCS.NS' else good.iloc[:0]) for s in kwargs['tickers']},axis=1)
    monkeypatch.setattr(market.yf,'download',download)
    first=await market.eod(2,3);assert 'TCS.NS' in first['errors'] and len(calls[0])==15
    second=await market.eod(2,3);assert calls[1]==['TCS.NS'] and not second['errors']
    before=market.observation(good,datetime(2026,1,19,14,0));assert before['session_date']=='2026-01-16'
    after=market.observation(good,datetime(2026,1,19,16,0));assert after['volume_multiple']==3 and len(after['baseline_sessions'])==10
    market.CACHE.clear()

def test_api_validation_and_controlled_503(monkeypatch):
    client=TestClient(app)
    assert client.get('/api/research/invalid!').status_code==422
    monkeypatch.setattr(r,'discover',AsyncMock(side_effect=RuntimeError('offline')))
    assert client.get('/api/research/ANYNSE?demo_fallback=false').status_code==503
    response=client.get('/api/research/ANYNSE');assert response.status_code==200 and response.json()['synthetic']

@pytest.mark.asyncio
async def test_host_rejected_before_request():
    with pytest.raises(ValueError):await r.fetch(None,'https://evil.example/document.pdf',r.APPROVED)

def test_decimal_boundaries_and_missing_metric_guidance():
    docs,data=r.fixtures('TCS');m=data.quarters[0].metrics['PAT'];m.guidance_low=m.guidance_high=None
    assert r.validate(data,docs)[0]['metrics']['PAT']['status']=='not comparable'
    parsed=r.parse_synthetic(docs);assert len(parsed.quarters)==4
    docs,data=r.fixtures('TCS');m=data.quarters[0].metrics['Revenue']
    m.guidance_quarter='FY2025 Q1'
    m.actual=Decimal('1025.01');m.quote='Revenue actual INR crore 1025.01.'
    docs[1]['text']+=' '+m.quote
    compared=r.validate(data,docs)[0]['metrics']['Revenue']
    assert compared['status']=='beat' and compared['delta']=='0.01'
    m.guidance_quarter='FY2024 Q4'
    with pytest.raises(ValueError):r.validate(data,docs)

@pytest.mark.asyncio
async def test_biography_enrichment_failure_preserves_source(monkeypatch):
    from backend.feed import enriched_feed
    monkeypatch.setenv('OPENAI_API_KEY','test-not-real')
    monkeypatch.setattr(r,'llm',AsyncMock(return_value={'facts':[{'text':'Invented Harvard education'}]}))
    result=await enriched_feed()
    card=next(x for x in result['material'] if x['category']=='management_change')
    assert card['biography']['summary']==biography()['summary']
    assert card['biography']['source_text']==BIO_SOURCE
    assert card['original_text']

@pytest.mark.asyncio
async def test_biography_separate_grounded_facts(monkeypatch):
    from backend.feed import enriched_feed
    monkeypatch.setenv('OPENAI_API_KEY','test-not-real')
    monkeypatch.setattr(r,'llm',AsyncMock(return_value={'facts':[{'text':'Meera Rao joined TCS in 2017'},{'text':'She holds an MBA from IIM Ahmedabad'}]}))
    result=await enriched_feed();card=next(x for x in result['material'] if x['category']=='management_change')
    assert 'model-extracted' in card['biography']['enrichment']
    assert card['biography']['summary'] not in BIO_SOURCE
