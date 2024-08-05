from typing import Any

from fastapi import Request

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


def log_extra(request: Request) -> dict[str, Any]:
    return {
        "request_method": request.method,
        "request_url": request.url.path,
        "request_query_params": dict(request.query_params),
        "request_headers": dict(request.headers),
    }


def str_to_bool(value: Any) -> bool:
    value = str(value)
    return value.lower() in {'1', 'true', 't', 'yes', 'y'}

