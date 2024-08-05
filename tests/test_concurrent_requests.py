import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from telicent_labels import TelicentModel

from telicent_lbapi.context import ModelContext
from telicent_lbapi.rest_service import create_app

from .helpers.custom_endpoints import AnotherModel, MyModel, custom_router

app, config = create_app(model_class=TelicentModel, custom_router=custom_router)


# @pytest.fixture(scope="module")
# def anyio_backend():
#     return 'asyncio'

@pytest.mark.asyncio
async def test_concurrent_requests(anyio_backend, monkeypatch):
    # track the model classes used
    model_classes = []

    def mock_set_model_class(model):
        model_classes.append(model)
        original_set_model_class(model)

    #  prevent recursion depth errors
    original_set_model_class = ModelContext.set_model_class
    monkeypatch.setattr(ModelContext, "set_model_class", mock_set_model_class)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tasks = []

        for _ in range(100):
            payload = {
                "identifier": "ItemA",
                "classification": "S",
                "permittedOrgs": ["ABC", "DEF", "HIJ"],
                "permittedNats": ["GBR", "FRA", "IRL"],
                "orGroups": ["Apple", "SOMETHING"],
                "andGroups": ["doctor", "admin"],
                "originator": "TestOriginator",
                "custodian": "TestCustodian",
                "policyRef": "TestPolicyRef",
                "dataSet": ["ds1", "ds2"],
                "authRef": ["ref1", "ref2"],
                "dispositionDate": "2023-01-01T23:59:59.003426-05:00",
                "dispositionProcess": "disp-process-1",
                "dissemination": ["news", "articles"]
            }
            tasks.append(ac.post("/api/v1/ingest", json=payload))

        for _ in range(100):
            tasks.append(ac.get("/custom/custom-endpoint-mymodel"))

        for _ in range(100):
            tasks.append(ac.get("/custom/custom-endpoint-anothermodel"))

        responses = await asyncio.gather(*tasks)

        # responses for /ingest endpoint
        for response in responses[:100]:
            assert response.status_code == 200
            assert response.json()["status"] == "success"

        # responses for /custom-endpoint-mymodel
        for response in responses[100:200]:
            assert response.status_code == 200
            assert response.json()["message"] == "This is a custom endpoint using MyModel"

        # responses for /custom-endpoint-anothermodel
        for response in responses[200:]:
            assert response.status_code == 200
            assert response.json()["message"] == f"This is a custom endpoint using {AnotherModel.__name__}"

    # count how many times context was set for each model
    ingest_count = sum(1 for model in model_classes if model == TelicentModel)
    mymodel_count = sum(1 for model in model_classes if model == MyModel)
    anothermodel_count = sum(1 for model in model_classes if model == AnotherModel)

    assert ingest_count == 300  # 300 cause middleware sets it after every response
    assert mymodel_count == 100
    assert anothermodel_count == 100
