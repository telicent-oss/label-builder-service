import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware
from starlette_context.plugins import RequestIdPlugin

from telicent_lbapi.api.v1 import router as api_router
from telicent_lbapi.context import ModelContext
from telicent_lbapi.core.api_config.config import load_config
from telicent_lbapi.core.api_config.log_config import configure_logging
from telicent_lbapi.core.middleware.context_middleware import ModelContextMiddleware

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


def create_app(model_class: type, custom_router: APIRouter = None):
    config = load_config()
    configure_logging(config)

    middleware = [
        Middleware(RawContextMiddleware, plugins=(RequestIdPlugin(),)),
        Middleware(ModelContextMiddleware, default_model_class=model_class)
    ]

    app = FastAPI(middleware=middleware)

    app.include_router(api_router, prefix="/api/v1")

    if custom_router:
        app.include_router(custom_router, prefix="/custom")

    ModelContext.set_model_class(model_class)

    @asynccontextmanager
    async def lifespan(ap: FastAPI):
        log.info(f"Starting {model_class.__name__} REST API service")
        log.info(f"Configuration: {config}")
        for route in ap.routes:
            if isinstance(route, APIRoute):
                log.info(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods}")
        yield
        log.info(f"Shutting down {model_class.__name__} REST API service")

    app.router.lifespan_context = lifespan

    return app, config


def run_api_service(model_class: type, custom_router: APIRouter = None):
    app, config = create_app(model_class, custom_router)
    uvicorn.run(app, host=config.server_host, port=config.server_port, log_config=None)
