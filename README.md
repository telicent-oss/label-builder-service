# label-builder-service

label-builder-service integrates with telicent-label-builder to allow wrapping a model in a rest-api
default endpoint is /api/v1/ingest which would convert a model to a label


## Installation

```shell
pip install telicent-label-builder-service
```

---

## Configuration

The application could only be configured through environment variables. When used in conjunction with 
telicent-label-builder there is no way to pass a configuration to rest_serivice.py->run_api_service

Configuration lives under `telicent-lbapi/api_config/config.py` and can be used for reference.

Supported env variables:

LOGGING_LEVEL - sets the log level for the REST Application - *Default*: `INFO`

CACHE_TIMEOUT - sets cache expiry time in seconds - *Default*: `5min`

RESTAPI_PORT - the port to run the server on - *Default*: `8000`

RESTAPI_HOST - the adress to run the server on - *Default*: `0.0.0.0`

LOG_TO_CONSOLE - propagates logs to STDOUT - *Default*: `true`

LOGING_DIR - logfile storage directory, path will be created, *ensure path is writable*

Default: UNIX systems - `/tmp/logs` Windows - `<TEMP>/logs`

LOG_FILENAME - filename to use for the log file - Default: `label-builder-service.log`

---

## Detail

Each request would be given a unique ID which is propagated in logs, the format is as follows:
```bash   
"%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d]" 
" [Request ID: %(request_id)s]"
" [Model Class: %(model_class)s] - %(message)s"
```

RequestID is preserved across the lifecycle of the request.
The library supports additional endpoints definitions, see USAGE below. There is a concept of model_class, this is 
usually the model that was implemented using the label builder. Any endpoints which do data validation would try and 
use that model unless specified otherwise by the "@set_model_class" decorator. When the decorator is used a middleware,
will revert the model back to the original one for this instance of the application.

e.g in the usage case below a call to `/custom-endpoint-failing` would use `MyModel` internally, after response is 
issued the model will be set back to `TelicentModel`.

The API provides a single endpoint `/api/v1/ingest` - it tries to convert a model instance to security labels, model
in use must implement `build_security_labels` method, otherwise the endpoint would fail.

In cases where no additional endpoints are required, a function to run the model as a service utilising the `/ingest` 
endpoint could be achieved by wrapping `run_api_service` in a class method within the model itself.

E.g:

```python
from telicent_lbapi.rest_service import run_api_service

class MyModel(TelicentMixin, BaseModel):
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
    
    @classmethod
    def run_as_api(cls):
        run_api_service(cls)
    
```

## Usage

```python
from fastapi import APIRouter, Request, HTTPException
from telicent_lbapi.context import ModelContext
from telicent_labels.telicent_model import TelicentMixin
from telicent_lbapi.services.label_builder_service import build_security_labels
from telicent_lbapi.decorators import set_model_class
from pydantic import BaseModel, ValidationError


class MyModel(TelicentMixin, BaseModel):
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


@custom_router.get("/custom-endpoint-failing")
@set_model_class(MyModel)
async def custom_endpoint_mymodel(request: Request):
    test_policy = {
        "testSth": "a",
        "classification": "b",
        "permittedOrgs": [
            "ABC",
        ],
        "permittedNats": [
            "GBR",
        ],
        "orGroups": [
            "Apple",
        ],
        "andGroups": [
            "doctor",
        ],
        "originator": "TestOriginator",
        "custodian": "TestCustodian",
        "policyRef": "TestPolicyRef"
    }
    try:
        labels = build_security_labels(data_header=test_policy)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"message": f"This is a custom endpoint using {MyModel.__name__}", "labels": labels}


@custom_router.get("/custom-endpoint-mymodel")
@set_model_class(MyModel)
async def custom_endpoint_mymodel(request: Request):
    test_policy = {
        "testSth": "a",
        "identifier": "sth",
        "classification": "b",
        "permittedOrgs": [
            "ABC",
        ],
        "permittedNats": [
            "GBR",
        ],
        "orGroups": [
            "Apple",
        ],
        "andGroups": [
            "doctor",
        ],
        "originator": "TestOriginator",
        "custodian": "TestCustodian",
        "policyRef": "TestPolicyRef"
    }
    try:
        labels = build_security_labels(data_header=test_policy)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"message": f"This is a custom endpoint using {MyModel.__name__}", "labels": labels}


@custom_router.get("/custom-endpoint-anothermodel")
@set_model_class(AnotherModel)
async def custom_endpoint_anothermodel(request: Request):
    return {"message": f"This is a custom endpoint using {ModelContext.get_model_class()}"}


if __name__ == "__main__":
    from telicent_labels import TelicentModel
    from telicent_lbapi.rest_service import run_api_service

    # TelicentModel used here just to illustrate the ability to switch models, the api is model driven.
    run_api_service(model_class=TelicentModel, custom_router=custom_router)

```