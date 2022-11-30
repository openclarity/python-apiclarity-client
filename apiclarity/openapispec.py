# Copyright © 2022 Cisco Systems, Inc. and its affiliates.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

# import openapi_spec_validator
from pydantic import AnyUrl, BaseModel, Extra, Field, InvalidDiscriminator, validator


class OASParameterIn(str, Enum):
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    FORMDATA = "formData"
    BODY = "body"


class OASSchemaType(str, Enum):
    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    NULL = "null"
    OBJECT = "object"
    STRING = "string"

    def isRecursiveType(self) -> bool:
        return self.value == self.ARRAY or self.value == self.OBJECT


class Contact(BaseModel):
    name: Optional[str] = Field(None, description="")
    url: Optional[str] = Field(None, description="")
    email: Optional[str] = Field(None, description="")


class License2(BaseModel):
    name: str = Field(description="")
    url: Optional[str] = Field(None, description="")


class License(License2):
    identifier: Optional[str] = Field(None, description="")


class Info2(BaseModel):
    title: str = Field(description="")
    description: Optional[str] = Field(None, description="")
    termsOfService: Optional[str] = Field(None, description="")
    contact: Optional[Contact] = Field(None, description="")
    license: Optional[License] = Field(None, description="")
    version: str = Field(description="")


class Info(Info2):
    summary: Optional[str] = Field(None, description="")


class OASSchema(BaseModel):
    ref: Optional[str] = Field(None, description="", alias="$ref")
    title: Optional[str] = Field(None, description="")
    descriminator: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    type: Union[List[OASSchemaType], OASSchemaType] = Field(
        OASSchemaType.STRING, description=""
    )
    required: Optional[List[str]] = Field(None, description="")
    readOnly: Optional[bool] = Field(None, description="")
    items: Optional["OASSchema"] = Field(None, description="")
    example: Any = Field(None, description="")
    properties: Optional[Dict[str, "OASSchema"]] = Field(None, description="")
    additionalProperties: Union[bool, "OASSchema", None] = Field(None, description="")

    class Config:
        extra = Extra.allow


class Header(BaseModel):
    type: str = Field(description="")
    description: Optional[str] = Field(None, description="")
    format: Optional[str] = Field(None, description="")

    class Config:
        extra = Extra.allow


class Parameter(BaseModel):
    name: str = Field(description="")
    oas_in: OASParameterIn = Field(description="", alias="in")
    description: Optional[str] = Field(None, description="")
    required: Optional[bool] = Field(None, description="")

    class Config:
        extra = Extra.allow


class Reference(BaseModel):
    ref: str = Field(description="", alias="$ref")


class OASResponse(BaseModel):
    description: str = Field(description="")
    oas_schema: Optional[OASSchema] = Field(None, description="", alias="schema")
    headers: Optional[Dict[str, Header]] = Field(None, description="")
    examples: Optional[Dict[str, Any]] = Field(None, description="")

    class Config:
        extra = Extra.allow


class OASTag(BaseModel):
    name: str = Field(description="")
    description: Optional[str] = Field(None, description="")
    # externalDocs:

    class Config:
        extra = Extra.allow


class OASOperation(BaseModel):
    tags: Optional[List[str]] = Field(None, description="")
    summary: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    operationId: Optional[str] = Field(None, description="")
    consumes: Optional[List[str]] = Field(None, description="")
    produces: Optional[List[str]] = Field(None, description="")
    parameters: Optional[List[Union[Parameter, Reference]]] = Field(
        None, description=""
    )
    responses: Dict[str, OASResponse] = Field(description="")
    schemes: Optional[List[str]] = Field(None, description="")
    deprecated: Optional[bool] = Field(None, description="")
    # security:

    class Config:
        extra = Extra.allow


class Path2(BaseModel):
    ref: Optional[str] = Field(None, description="", alias="$ref")
    get: Optional[OASOperation] = Field(None, description="")
    put: Optional[OASOperation] = Field(None, description="")
    post: Optional[OASOperation] = Field(None, description="")
    delete: Optional[OASOperation] = Field(None, description="")
    options: Optional[OASOperation] = Field(None, description="")
    head: Optional[OASOperation] = Field(None, description="")
    patch: Optional[OASOperation] = Field(None, description="")
    parameters: Optional[List[Union[Parameter, Reference]]] = Field(
        None, description=""
    )

    def operations(self) -> Generator[Tuple[str, OASOperation], None, None]:
        for op in ["get", "put", "post", "delete", "options", "head", "patch"]:
            opval = getattr(self, op)
            if opval is not None:
                yield op, opval

    class Config:
        extra = Extra.allow


class Path3(Path2):
    summary: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    trace: Optional[OASOperation] = Field(None, description="")


class OpenAPI2(BaseModel):
    info: Info2 = Field(description="")
    swagger: str = Field(description="")
    host: Optional[str] = Field(None, description="")
    basePath: Optional[str] = Field(None, description="")
    schemes: Optional[List[str]] = Field(None, description="")
    consumes: Optional[List[str]] = Field(None, description="")
    produces: Optional[List[str]] = Field(None, description="")
    paths: Dict[str, Path2] = Field(description="")
    definitions: Dict[str, OASSchema] = Field({}, description="")
    parameters: Optional[Dict[str, Parameter]] = Field(None, description="")
    responses: Optional[Dict[str, OASResponse]] = Field(None, description="")
    # securityDefinitions:
    # security:
    tags: Optional[List[OASTag]] = Field(None, description="")
    # externalDocs:

    @property
    def version(self) -> str:
        return self.info.version

    @validator("paths")
    def path_starts_with_slash(cls, paths: Dict[str, Path2]) -> Dict[str, Path2]:
        for path in paths.keys():
            if not path.startswith("/"):
                raise ValueError(f'path "{path}" MUST begin with a /')
        return paths

    class Config:
        extra = Extra.allow


class OASServer(BaseModel):
    url: str = Field(description="")
    description: Optional[str] = Field(None, description="")
    # variables: Optional[Dict[str,OASServerVariable]] = Field(None, description="")

    class Config:
        extra = Extra.allow


class OpenAPI3(BaseModel):
    info: Info = Field(description="")
    openapi: str = Field(description="")
    jsonSchemaDialect: Optional[AnyUrl] = Field(None, description="")
    servers: List[OASServer] = Field([OASServer(url="/")], description="")
    tags: Optional[List[OASTag]] = Field(None, description="")
    paths: Dict[str, Path3] = Field(description="")

    @validator("servers", pre=True)
    def servers_default_value(cls, v: Any) -> Any:
        if v is None or (isinstance(v, List) and len(v) == 0):
            return [OASServer(url="/")]
        else:
            return v

    @property
    def version(self) -> str:
        return self.info.version

    class Config:
        extra = Extra.allow


def build_openapi_model(
    apiSpec: Dict[str, Any], validate: bool = False
) -> Union[OpenAPI2, OpenAPI3]:
    if "swagger" in apiSpec:
        # if validate:
        #    openapi_spec_validator.validate_v2_spec(apiSpec)
        return OpenAPI2.parse_obj(apiSpec)
    elif "openapi" in apiSpec:
        # if validate:
        #    openapi_spec_validator.validate_v30_spec(apiSpec)
        return OpenAPI3.parse_obj(apiSpec)
    else:
        raise InvalidDiscriminator(
            discriminator_key="openapi",
            discriminator_value=None,
            allowed_values=["3.1.0"],
        )
