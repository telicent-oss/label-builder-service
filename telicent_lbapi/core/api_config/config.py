import os
import platform
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from telicent_lib.config import Configurator

from telicent_lbapi.utils.helpers import str_to_bool

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

log_filename_default = 'label-builder-service.log'


def default_root_dir():
    system = platform.system()
    if system in ['Linux', 'Darwin']:
        log_root_dir_default = Path('/tmp/logs')
    elif system == 'Windows':
        log_root_dir_default = Path(os.getenv('TEMP')) / 'logs'
    else:
        raise OSError("Unsupported operating system. Try setting log directory manually.")

    return log_root_dir_default


@dataclass
class ApiConfig:
    logging_level: str
    cache_size: int
    cache_timeout: int
    server_port: int
    server_host: str
    log_to_console: bool
    log_dir: Path
    log_filename: str
    log_to_file: bool


def load_config() -> ApiConfig:
    load_dotenv()
    config = Configurator()
    logging_level = config.get(
        "LOGGING_LEVEL", "INFO"
    )
    cache_size = config.get(
        "CACHE_SIZE", default=1000000
    )
    cache_timeout = config.get(
        "CACHE_TIMEOUT", default=300
    )
    server_port = config.get(
        "RESTAPI_PORT", default=8000
    )
    server_host = config.get(
        "RESTAPI_HOST", default="0.0.0.0"
    )
    log_to_console = config.get(
        "LOG_TO_CONSOLE", default=True
    )
    log_dir = config.get(
        "LOGGING_DIR", default=default_root_dir()
    )
    log_filename = config.get(
        "LOG_FILENAME", default=log_filename_default
    )
    log_to_file = config.get("LOG_TO_FILE", default=False)

    return ApiConfig(
        logging_level=logging_level,
        cache_size=cache_size,
        cache_timeout=cache_timeout,
        server_port=int(server_port),
        server_host=server_host,
        log_to_console=str_to_bool(log_to_console),
        log_dir=Path(log_dir),
        log_filename=log_filename,
        log_to_file=str_to_bool(log_to_file)
    )
