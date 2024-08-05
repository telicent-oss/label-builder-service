import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from telicent_lbapi.utils.cache import get_cached_labels
from telicent_lbapi.utils.helpers import log_extra

__license__ = """
Copyright (c) Telicent Ltd.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

log = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def ingest_data_header(request: Request):
    try:
        data_header = await request.json()
    except Exception as e:
        log.exception("Error processing request.", exc_info=e)
        raise HTTPException(status_code=400, detail="Error processing request.") from e

    try:
        security_label = await get_cached_labels(data_header)
    except ValidationError as e:
        log.error("Validation error occurred.", exc_info=e)
        raise HTTPException(status_code=400, detail="Validation error occurred.") from e
    except ValueError as e:
        log.error("Failed to build security labels.", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        log.error("An unexpected error occurred.", exc_info=e)
        raise HTTPException(status_code=500, detail="Internal server error") from e

    log.info("Request - ok", extra=log_extra(request))
    return {"status": "success", "security_label": security_label}


@router.get("/status")
async def get_status():
    return {"status": "OK"}
