import os,re
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .feed import feed,enriched_feed
from .market import eod
from .network import search
from .research import research
load_dotenv('backend/.env')
# Render supplies the deployed origin; an explicit user setting takes precedence.
if os.getenv('RENDER_EXTERNAL_URL'):
    os.environ.setdefault('ALLOWED_ORIGINS', os.environ['RENDER_EXTERNAL_URL'])
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

def mount_frontend(application, directory):
    """Register static hosting last so API routes retain precedence."""
    directory=Path(directory)
    if (directory/'index.html').is_file():
        application.mount('/',StaticFiles(directory=str(directory),html=True),name='frontend')
        return True
    return False

mount_frontend(app,os.getenv('FRONTEND_DIST',str(Path(__file__).resolve().parent.parent/'frontend'/'out')))
