import logging

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from telicent_labels import TelicentModel

from telicent_lbapi.rest_service import create_app

from .helpers.custom_endpoints import custom_router


@pytest.fixture(autouse=True)
def suppress_logging(caplog):
    caplog.set_level(logging.ERROR)


@pytest.fixture(scope="module")
def app():
    app, _ = create_app(model_class=TelicentModel, custom_router=custom_router)
    return app


@pytest.fixture
async def async_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as client:
        yield client
