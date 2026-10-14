from pathlib import Path

import pytest
from playwright.sync_api import expect

OUTPUT = Path('output/playwright')


def open_catalog(page, base_url):
    page.goto(base_url)
    expect(page.locator('.planet-card')).to_have_count(7)


def test_desktop_and_assets(page, base_url):
    errors = []
    failed_requests = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('requestfailed', lambda request: failed_requests.append(request.url))
    open_catalog(page, base_url)
    expect(page.get_by_role('heading', name='Миры галактики.')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    assert errors == []
    assert failed_requests == []
    OUTPUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUTPUT / 'desktop.png'), full_page=True)


def test_search_and_region(page, base_url):
    open_catalog(page, base_url)
    page.get_by_role('searchbox').fill('ТАТУИН')
    expect(page.locator('.planet-card')).to_have_count(1)
    expect(page.locator('.planet-card h3')).to_have_text('Татуин')
    page.get_by_label('Регион', exact=True).select_option('core')
    expect(page.locator('.planet-card')).to_have_count(0)
    expect(page.get_by_role('status')).to_contain_text('Ничего не найдено')
    page.get_by_role('searchbox').fill('')
    expect(page.locator('.planet-card h3')).to_have_text('Корусант')
    page.get_by_label('Регион', exact=True).select_option('')
    expect(page.locator('.planet-card')).to_have_count(7)


def test_error_and_retry(page, base_url):
    page.route('**/api/planets?*', lambda route: route.fulfill(status=503, body='unavailable'))
    page.goto(base_url)
    expect(page.get_by_role('status')).to_contain_text('Связь с атласом потеряна')
    expect(page.get_by_role('button', name='Повторить загрузку')).to_be_visible()
    page.unroute('**/api/planets?*')
    page.get_by_role('button', name='Повторить загрузку').click()
    expect(page.locator('.planet-card')).to_have_count(7)
    expect(page.get_by_role('button', name='Повторить загрузку')).to_be_hidden()


@pytest.mark.parametrize('width', [375, 390, 640])
@pytest.mark.xfail(strict=True, reason='UI-001: intentional mobile catalog overflow; see docs/mentor.md')
def test_mobile_has_no_horizontal_overflow(page, base_url, width):
    page.set_viewport_size({'width': width, 'height': 844})
    open_catalog(page, base_url)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUTPUT / f'mobile-{width}.png'), full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Catalog exceeds mobile viewport'


def test_tablet_has_no_horizontal_overflow(page, base_url):
    page.set_viewport_size({'width': 768, 'height': 1024})
    open_catalog(page, base_url)
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
