import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'service': 'galaxy-atlas'}


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert '<html lang="ru">' in response.text
    assert 'id="planet-grid"' in response.text


@pytest.mark.parametrize('asset,mime', [
    ('styles.css', 'text/css'), ('app.js', 'javascript'), ('favicon.svg', 'image/svg+xml'),
])
def test_static_assets(client, asset, mime):
    response = client.get(f'/static/{asset}')
    assert response.status_code == 200
    assert mime in response.headers['content-type']
    assert len(response.content) > 100


def test_catalog_contract(client):
    response = client.get('/api/planets')
    assert response.status_code == 200
    planets = response.json()
    assert len(planets) == 7
    assert len({p['id'] for p in planets}) == 7
    assert all(set(p) == {'id', 'name', 'region', 'terrain', 'description', 'color', 'moons'} for p in planets)


@pytest.mark.parametrize('query,ids', [
    ('  ТАТУИН  ', ['tatooine']), ('hoth', ['hoth']),
    ('болота', ['dagobah']), ('нет-такой-планеты', []),
    ('Камино', ['kamino']), ('Корусант', ['coruscant']),
])
def test_search(client, query, ids):
    response = client.get('/api/planets', params={'q': query})
    assert response.status_code == 200
    assert [p['id'] for p in response.json()] == ids


def test_region_and_query_are_combined(client):
    assert [p['id'] for p in client.get('/api/planets?region=core').json()] == ['coruscant']
    assert client.get('/api/planets', params={'region': 'core', 'q': 'Татуин'}).json() == []


@pytest.mark.parametrize('params', [{'region': 'invalid'}, {'q': 'x' * 101}])
def test_invalid_filters(client, params):
    assert client.get('/api/planets', params=params).status_code == 422


def test_planet_detail_and_missing_planet(client):
    response = client.get('/api/planets/tatooine')
    assert response.status_code == 200
    assert response.json()['name'] == 'Татуин'
    assert client.get('/api/planets/not-a-planet').status_code == 404


def test_missing_static_is_404(client):
    assert client.get('/static/missing.css').status_code == 404
