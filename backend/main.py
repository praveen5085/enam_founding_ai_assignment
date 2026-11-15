import os,re
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from .feed import feed,enriched_feed
from .market import eod
from .network import search
from .research import research
load_dotenv('backend/.env')
app=FastAPI(title='FINN',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),allow_methods=['GET'],allow_headers=['*'])
@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/api/feed')
async def get_feed(hours:int=Query(24,ge=1,le=168)): return await enriched_feed(hours)
@app.get('/api/network')
def get_network(q:str=Query('',max_length=200)):
    f=feed(24);return search(q,events=f['material']+f['routine'])
@app.get('/api/eod')
async def get_eod(vol_threshold:float=Query(2,gt=0,le=100),price_threshold:float=Query(3,ge=0,le=100)): return await eod(vol_threshold,price_threshold)
@app.get('/api/research/{ticker}')
async def get_research(ticker:str,demo_fallback:bool=True):
    ticker=ticker.upper().removesuffix('.NS')
    if not re.fullmatch(r'[A-Z0-9][A-Z0-9&_-]{0,29}',ticker): raise HTTPException(422,'Invalid NSE ticker')
    try: return await research(ticker,demo_fallback)
    except ValueError as exc: raise HTTPException(503,str(exc)) from exc
