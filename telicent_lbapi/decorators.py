import logging
from collections.abc import Callable
from functools import wraps

from fastapi import Request

from telicent_lbapi.context import ModelContext

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


def set_model_class(model_class: type) -> Callable:
    """
    Allows to temporary change the model class endpoints operate on,
    on response API's middleware resets the model class to the one
    rest-service was initialised with
    :param model_class:
    :return:
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            log.info(f"Model class changed to: {model_class} via decorator.")
            ModelContext.set_model_class(model_class)
            return await func(request, *args, **kwargs)
        return wrapper

    return decorator
