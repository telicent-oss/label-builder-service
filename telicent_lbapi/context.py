import contextvars

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

model_class: contextvars.ContextVar[type] = contextvars.ContextVar("model_class")


class ModelContext:
    @classmethod
    def set_model_class(cls, model: type):
        model_class.set(model)

    @classmethod
    def get_model_class(cls) -> type:
        return model_class.get()
