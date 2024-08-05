import asyncio
import contextvars

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


def build_security_labels(data_header: dict):
    model_class = ModelContext.get_model_class()
    if model_class is None:
        raise ValueError("Model class is not set in the context.")
    model_instance = model_class(**data_header)
    return model_instance.build_security_labels()


async def async_build_security_labels(data_header: dict):
    loop = asyncio.get_running_loop()
    # context needs manually copied
    ctx = contextvars.copy_context()
    return await loop.run_in_executor(None, ctx.run, build_security_labels, data_header)
