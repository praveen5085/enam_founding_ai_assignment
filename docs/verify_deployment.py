"""HTTP smoke checks for the actual hosted FINN application (not browser QA).

Usage: python -m docs.verify_deployment https://your-service.onrender.com
"""
import argparse
import re
from urllib.parse import urlparse

import httpx


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    args=parser.parse_args()
    origin=args.url.rstrip('/')
    if urlparse(origin).scheme not in {'http','https'}:
        parser.error('Provide the full http:// or https:// service URL')
    with httpx.Client(base_url=origin,timeout=180,follow_redirects=True) as client:
        health=client.get('/health')
        health.raise_for_status()
        assert health.json()['status']=='ok'
        page=client.get('/')
        page.raise_for_status()
        assert 'Clarity in the noise' in page.text
        scripts=re.findall(r'<script[^>]+src="([^"]+)"',page.text)
        assert scripts,'No frontend scripts found'
        for script in scripts:
            # Build assets must stay on the app origin.
            assert script.startswith('/_next/')
            response=client.get(script)
            response.raise_for_status()
            assert 'javascript' in response.headers.get('content-type','')
        feed=client.get('/api/feed?hours=168')
        feed.raise_for_status()
        data=feed.json()
        assert len(data['material'])+len(data['routine'])==10
        network=client.get('/api/network?q=Pharma%20or%20IT')
        network.raise_for_status()
        assert network.json()['profiles']
        research=client.get('/api/research/TCS')
        research.raise_for_status()
        analysis=research.json()
        assert 1<=len(analysis['quarters'])<=4
        assert analysis['evidence_mode']
        print(f'PASS {origin}: health, frontend, {len(scripts)} JavaScript assets, feed, network and research')
        print(f"Research: {analysis['evidence_mode']}; narrative {analysis['narrative_state']}")


if __name__=='__main__':
    main()
