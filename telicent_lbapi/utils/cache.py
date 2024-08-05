import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta

from cachetools import LRUCache
from pydantic import ValidationError

from telicent_lbapi.core.api_config.config import load_config
from telicent_lbapi.services.label_builder_service import async_build_security_labels

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

conf = load_config()
CACHE_SIZE: int = int(conf.cache_size)
CACHE_TIMEOUT: int = conf.cache_timeout
cache_store: LRUCache = LRUCache(maxsize=CACHE_SIZE)
cache_lock: asyncio.Lock = asyncio.Lock()


def clear_cache():
    global cache_store
    cache_store.clear()


def hash_dict(data: dict) -> str:
    sorted_data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(sorted_data_str.encode()).hexdigest()


async def get_cached_labels(header_data: dict):
    cache_key = hash_dict(header_data)

    async with cache_lock:
        if cache_key in cache_store:
            cached_value, expiry_time = cache_store[cache_key]
            if datetime.now() < expiry_time:
                logging.debug(f"Cache entry found. {cache_key=}, {expiry_time=}")
                return cached_value

        try:
            security_labels = await async_build_security_labels(data_header=header_data)
        except ValidationError as e:
            log.error("Validation error occurred while building security labels.", exc_info=e)
            raise
        except Exception as e:
            log.error("An error occurred while building security labels.", exc_info=e)
            raise

        cache_data = (security_labels, datetime.now() + timedelta(seconds=CACHE_TIMEOUT))
        log.debug(f"Adding new key to cache={cache_key}, relative expiry={cache_data[1]}")

        cache_store[cache_key] = cache_data

    return security_labels
