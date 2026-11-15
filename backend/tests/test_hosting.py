from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.main import mount_frontend


def test_frontend_assets_and_api_share_origin(tmp_path):
    (tmp_path/'index.html').write_text('<h1>FINN</h1>',encoding='utf-8')
    (tmp_path/'_next').mkdir()
    (tmp_path/'_next'/'app.js').write_text('console.log("FINN")',encoding='utf-8')
    app=FastAPI()

    @app.get('/api/health')
    def health():
        return {'status':'ok'}

    assert mount_frontend(app,tmp_path)
    client=TestClient(app)
    assert client.get('/').text=='<h1>FINN</h1>'
    assert client.get('/_next/app.js').status_code==200
    assert client.get('/api/health').json()=={'status':'ok'}
    assert client.get('/missing').status_code==404
    assert client.get('/../backend/.env').status_code==404


def test_missing_export_does_not_mount(tmp_path):
    assert not mount_frontend(FastAPI(),tmp_path)
