import logging

from starlette.types import ASGIApp, Receive, Scope, Send

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


class ModelContextMiddleware:
    def __init__(self, app: ASGIApp, default_model_class: type):
        self.app = app
        self.default_model_class = default_model_class

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    ModelContext.set_model_class(self.default_model_class)
                    log.debug(f"Model class reverted to default in middleware: "
                              f"{ModelContext.get_model_class().__name__}")
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)
