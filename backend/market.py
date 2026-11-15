import asyncio,time
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import yfinance as yf

SYMBOLS='RELIANCE TCS HDFCBANK INFY SUNPHARMA TATAMOTORS ULTRATECH BHARTIARTL ASIANPAINT LT ITC BAJFINANCE MARUTI TITAN ZOMATO'.split()
ALIASES={'ULTRATECH':'ULTRACEMCO','ZOMATO':'ETERNAL','TATAMOTORS':'TMPV'}
CACHE={}

def observation(frame,now):
    f=frame.dropna(subset=['Close','Volume']).copy()
    completed=[]
    for idx in f.index:
        day=pd.Timestamp(idx).date()
        if day<now.date() or (day==now.date() and (now.hour,now.minute)>=(15,30)): completed.append(idx)
    f=f.loc[completed]
    if len(f)<11: raise ValueError('Need eleven completed sessions')
    current=f.iloc[-1];base=float(f.iloc[-11:-1]['Volume'].mean())
    if base<=0: raise ValueError('Nonpositive volume baseline')
    return dict(session_date=str(pd.Timestamp(f.index[-1]).date()),baseline_sessions=[str(pd.Timestamp(x).date()) for x in f.index[-11:-1]],close=float(current['Close']),volume=int(current['Volume']),volume_multiple=float(current['Volume'])/base,price_change=(float(current['Close'])/float(f.iloc[-2]['Close'])-1)*100)

async def eod(vol_threshold,price_threshold):
    now=datetime.now(ZoneInfo('Asia/Kolkata')); errors={}; observations=[]
    missing=[s for s in SYMBOLS if s not in CACHE or time.monotonic()-CACHE[s][0]>300]
    if missing:
        providers=[ALIASES.get(s,s)+'.NS' for s in missing]
        try:
            batch=await asyncio.to_thread(yf.download,tickers=providers,period='1mo',group_by='ticker',auto_adjust=False,progress=False,threads=True)
            for symbol,provider in zip(missing,providers):
                try:
                    frame=batch[provider] if isinstance(batch.columns,pd.MultiIndex) else batch
                    value=observation(frame,now);CACHE[symbol]=(time.monotonic(),value)
                except Exception as exc: errors[symbol+'.NS']=str(exc)
        except Exception as exc:
            errors.update({s+'.NS':str(exc) for s in missing})
    for s in SYMBOLS:
        if s in CACHE:
            v=CACHE[s][1]
            observations.append(dict(symbol=s+'.NS',provider_symbol=ALIASES.get(s,s)+'.NS',**v,volume_alert=v['volume_multiple']>vol_threshold,price_alert=abs(v['price_change'])>price_threshold))
    return dict(observations=observations,errors=errors,timezone='Asia/Kolkata',synthetic=False)
