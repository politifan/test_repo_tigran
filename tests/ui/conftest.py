import socket
import threading
import time

import pytest
import uvicorn
from playwright.sync_api import sync_playwright

from app.main import app


@pytest.fixture(scope='session')
def base_url():
    # Let the OS pick a free port; keep the socket until Uvicorn takes it.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level='warning'))
        thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
        thread.start()
        try:
            deadline = time.monotonic() + 10
            while not server.started:
                if not thread.is_alive() or time.monotonic() > deadline:
                    raise RuntimeError('Test server failed to start')
                time.sleep(.05)
            yield f'http://127.0.0.1:{port}'
        finally:
            server.should_exit = True
            thread.join(timeout=10)


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
    page = context.new_page()
    yield page
    context.close()
