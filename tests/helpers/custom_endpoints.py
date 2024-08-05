from fastapi import APIRouter, Request
from telicent_labels.telicent_model import TelicentMixin

from telicent_lbapi.decorators import set_model_class
from telicent_lbapi.services.label_builder_service import build_security_labels


class MyModel(TelicentMixin):
    testSth: str | None = "sth"
    identifier: str
    classification: str
    orGroups: list[str]
    andGroups: list[str]
    permittedOrgs: list[str]
    permittedNats: list[str]

    def additional_method(self):
        print("Custom functionality here")

    def build_security_labels(self):
        return {"labels": "custom"}


class AnotherModel:
    def additional_method(self):
        print("Another custom functionality here")

    def build_security_labels(self):
        return {"labels": "another_custom"}


custom_router = APIRouter()


@custom_router.get("/custom-endpoint-mymodel")
@set_model_class(MyModel)
async def custom_endpoint_mymodel(request: Request):
    test_policy = {
        "testSth": "a",
        "identifier": "test",
        "classification": "b",
        "permittedOrgs": ["ABC"],
        "permittedNats": ["GBR"],
        "orGroups": ["Apple"],
        "andGroups": ["doctor"],
        "originator": "TestOriginator",
        "custodian": "TestCustodian",
        "policyRef": "TestPolicyRef"
    }
    labels = build_security_labels(data_header=test_policy)
    return {"message": f"This is a custom endpoint using {MyModel.__name__}", "labels": labels}


@custom_router.get("/custom-endpoint-anothermodel")
@set_model_class(AnotherModel)
async def custom_endpoint_anothermodel(request: Request):
    return {"message": f"This is a custom endpoint using {AnotherModel.__name__}"}
