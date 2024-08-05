import logging
import os
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError

from telicent_lbapi.context import ModelContext
from telicent_lbapi.core.api_config.config import ApiConfig

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


class ModelClassFilter(logging.Filter):
    def filter(self, record):
        try:
            model_class = ModelContext.get_model_class()
            record.model_class = model_class.__name__
        except AttributeError:
            record.model_class = 'N/A'
        except LookupError:
            record.model_class = 'UNKNOWN'
        return True


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = context.data.get("X-Request-ID", "unknown")
        except ContextDoesNotExistError:
            record.request_id = "N/A"

        return True


def configure_logging(config: ApiConfig):
    log_to_console = config.log_to_console
    log_level = logging.getLevelName(config.logging_level)
    log_dir = config.log_dir
    log_filename = config.log_filename

    log_file = log_dir / log_filename
    log_file.parent.mkdir(parents=True, exist_ok=True)

    if os.getenv('LABEL_BUILDER_SERVICE_DEBUG', False):
        log_level = logging.DEBUG

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    request_id_filter = RequestIdFilter()
    model_class_filter = ModelClassFilter()

    console_handler = logging.StreamHandler()

    if log_to_console:
        console_handler.setLevel(log_level)
        console_handler.addFilter(request_id_filter)
        console_handler.addFilter(model_class_filter)
        console_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d]"
            " [Request ID: %(request_id)s]"
            " [Model Class: %(model_class)s] - %(message)s"
        ))
        root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        filename=str(log_file), maxBytes=1024 * 1024 * 4, backupCount=3
    )
    file_handler.setLevel(log_level)
    file_handler.addFilter(request_id_filter)
    file_handler.addFilter(model_class_filter)

    keys_to_log = [
        'asctime',
        'created',
        'levelname',
        'filename',
        'funcName',
        'lineno',
        'message',
        'processName',
        'threadName',
        'request_id',
        'model_class'
    ]

    def log_format(keys):
        return [f'%({i:s})s' for i in keys]

    custom_format = ' '.join(log_format(keys_to_log))
    json_formatter = jsonlogger.JsonFormatter(custom_format)
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
