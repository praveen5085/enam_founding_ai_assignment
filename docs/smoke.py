"""Optional real provider probes; never a regression-test dependency."""
import asyncio
from backend.market import eod
from backend.research import discover

async def main():
    market=await eod(2,3)
    print('Yahoo successful observations:',len(market['observations']))
    print('Yahoo errors:',market['errors'])
    try:
        docs=await discover('TCS')
        print('Primary documents discovered:',len(docs))
        print('URLs:',[d['url'] for d in docs])
    except Exception as exc: print('Live research discovery unavailable:',type(exc).__name__,str(exc))

if __name__=='__main__':asyncio.run(main())
