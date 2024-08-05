import pytest

from telicent_lbapi.utils.cache import clear_cache


@pytest.fixture(autouse=True)
def run_around_tests():
    clear_cache()
    yield
    clear_cache()


@pytest.mark.asyncio
async def test_ingest_endpoint(async_client):
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

    response = await async_client.post("/api/v1/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_custom_endpoint_mymodel(async_client):
    response = await async_client.get("/custom/custom-endpoint-mymodel")
    assert response.status_code == 200
    assert response.json()["message"] == "This is a custom endpoint using MyModel"


@pytest.mark.asyncio
async def test_custom_endpoint_anothermodel(async_client):
    response = await async_client.get("/custom/custom-endpoint-anothermodel")
    assert response.status_code == 200
    assert response.json()["message"] == "This is a custom endpoint using AnotherModel"


@pytest.mark.asyncio
async def test_ingest_invalid_payload(async_client):
    payload = {"invalid": "data"}

    response = await async_client.post("/api/v1/ingest", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Validation error occurred."
