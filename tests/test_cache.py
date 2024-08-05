from datetime import datetime, timedelta

import pytest

from telicent_lbapi.utils.cache import cache_store, clear_cache


@pytest.fixture(autouse=True)
def run_around_tests():
    clear_cache()
    yield
    clear_cache()


@pytest.mark.asyncio
async def test_cache_hits(async_client):
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

    assert len(cache_store) == 1

    response = await async_client.post("/api/v1/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    assert len(cache_store) == 1


@pytest.mark.asyncio
async def test_cache_expiration(async_client):
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

    assert len(cache_store) == 1

    for key in cache_store:
        cache_store[key] = (cache_store[key][0], datetime.now() - timedelta(seconds=1))

    response = await async_client.post("/api/v1/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(cache_store) == 1


@pytest.mark.asyncio
async def test_cache_miss(async_client):
    payload_1 = {
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

    payload_2 = {
        "identifier": "ItemB",
        "classification": "S",
        "permittedOrgs": ["XYZ"],
        "permittedNats": ["USA"],
        "orGroups": ["Orange"],
        "andGroups": ["teacher"],
        "originator": "TestOriginatorB",
        "custodian": "TestCustodianB",
        "policyRef": "TestPolicyRefB",
        "dataSet": ["ds3"],
        "authRef": ["ref3"],
        "dispositionDate": "2023-01-01T23:59:59.003426-05:00",
        "dispositionProcess": "disp-process-2",
        "dissemination": ["blogs"]
    }

    response = await async_client.post("/api/v1/ingest", json=payload_1)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    assert len(cache_store) == 1

    response = await async_client.post("/api/v1/ingest", json=payload_2)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    assert len(cache_store) == 2
