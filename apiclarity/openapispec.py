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

import re
from enum import Enum
from typing import Any, Dict, Generator, List, Literal, Optional, Tuple, Union

# import openapi_spec_validator
from pydantic import AnyUrl, BaseModel, Extra, Field, InvalidDiscriminator, validator


class OASParameterIn(str, Enum):
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    FORMDATA = "formData"
    BODY = "body"
    COOKIE = "cookie"


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

    @validator("email")
    def validate_email(cls, v: str) -> str:
        regex = re.compile(r"^\S+@\S+\.\S+$")
        if regex.match(v) is None:
            raise ValueError(f"Contact email not valid: {v}")
        return v


class License2(BaseModel):
    name: str = Field(description="")
    url: Optional[str] = Field(None, description="")


class License(License2):
    identifier: Optional[str] = Field(None, description="")


class OASServerVariable(BaseModel):
    """An object representing a Server Variable for server URL template
    substitution.

    Reference: OpenAPI 3.1
    """

    oas_enum: Optional[List[str]] = Field(
        None,
        alias="enum",
        description="An enumeration of string values to be used if the substitution"
        " options are from a limited set.",
    )
    default: str = Field(
        description="The default value to use for substitution, which SHALL be"
        " sent if an alternate value is not supplied."
    )
    description: Optional[str] = Field(
        None, description="An optional description for the server variable."
    )


class OASServer(BaseModel):
    """
    An object representing a Server.

    Reference: OpenAPI 3.1
    """

    url: str = Field(description="A URL to the target host.")
    description: Optional[str] = Field(
        None,
        description="An optional string describing the host designated by the URL.",
    )
    variables: Optional[Dict[str, OASServerVariable]] = Field(
        None, description="A map between a variable name and its value."
    )


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
    # TODO: OASSchema3 needs to be redone
    ref: Optional[str] = Field(None, description="", alias="$ref")
    title: Optional[str] = Field(None, description="")
    discriminator: Optional[str] = Field(None, description="")
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


class OASExternalDocument(BaseModel):
    """Allows referencing an external resource for extended documentation

    Reference: OpenAPI 3.1
    """

    description: Optional[str] = Field(
        None, description="A description of the target documentation."
    )
    url: str = Field(description="The URL for the target documentation")


class OASTag(BaseModel):
    """Adds metadata to a single tag that is used by the Operation Object.

    Reference: OpenAPI 3.1
    """

    name: str = Field(description="The name of the tag.")
    description: Optional[str] = Field(None, description="A description for the tag.")
    externalDocs: Optional[OASExternalDocument] = Field(
        None, description="Additional external documentation for this tag."
    )


class OASExample(BaseModel):
    """In all cases, the example value is expected to be compatible with the type
    schema of its associated value.

    Reference: OpenAPI 3.1
    """

    summary: Optional[str] = Field(
        None, description="Short description for the example."
    )
    description: Optional[str] = Field(
        None, description="Long description for the example."
    )
    value: Optional[Any] = Field(None, description="Embedded literal example.")
    externalValue: Optional[Any] = Field(
        None, description="A URI that points to the literal example."
    )


class OASEncoding(BaseModel):
    """A single encoding definition applied to a single schema property.

    Reference: OpenAPI 3.1
    """

    contentType: Optional[str] = Field(
        None, description="The Content-Type for encoding a specific property."
    )
    headers: Optional[Dict[str, Union[Header, Reference]]] = Field(
        None,
        description="A map allowing additional information to be provided"
        " as headers.",
    )
    style: Optional[str] = Field(
        None,
        description="Describes how a specific property value will be serialized"
        " depending on its type.",
    )
    explode: Optional[bool] = Field(
        None,
        description="When this is true, property values of type array or object"
        " generate separate parameters for each value of the array,"
        " or key-value-pair of the map.",
    )
    allowReserved: bool = Field(
        False,
        description="Determines whether the parameter value SHOULD allow reserved"
        " characters, as defined by [RFC3986]",
    )


class OASMediaType(BaseModel):
    """Each Media Type Object provides schema and examples for the media type
    identified by its key.

    Reference: OpenAPI 3.1
    """

    # TODO: because OASSchema was significantly refactored, we accept any for now
    oas_schema: Optional[Union[Reference, Any]] = Field(
        None,
        alias="schema",
        description="The schema defining the content of the request,"
        " response, or parameter.",
    )
    example: Optional[Any] = Field(None, description="Example of the media type.")
    examples: Optional[Dict[str, Union[OASExample, Reference]]] = Field(
        None, description="Examples of the media type."
    )
    encoding: Optional[Dict[str, OASEncoding]] = Field(
        None, description="A map between a property name and its encoding information."
    )


class OASLink(BaseModel):
    """The Link object represents a possible design-time link for a response.

    Reference: OpenAPI 3.1
    """

    operationRef: Optional[str] = Field(
        "", description="A relative or absolute URI reference to an OAS operation."
    )
    operationId: Optional[str] = Field(
        "",
        description="The name of an existing, resolvable OAS operation, as"
        " defined with a unique operationId.",
    )
    parameters: Optional[Dict[str, str]] = Field(
        None,
        description="A map representing parameters to pass to an operation as"
        " specified with operationId or identified via operationRef.",
    )
    requestBody: Optional[Any] = Field(
        None,
        description="A literal value or {expression} to use as a request body"
        " when calling the target operation.",
    )
    description: Optional[str] = Field(None, description="A description of the link.")
    server: Optional[OASServer] = Field(
        None, description="A server object to be used by the target operation."
    )


class OASResponse3(OASResponse):
    """Describes a single response from an API Operation, including design-time,
    static links to operations based on the response.

    Reference: OpenAPI 3.1
    """

    content: Optional[Dict[str, OASMediaType]] = Field(
        None,
        description="A map containing descriptions of potential response payloads.",
    )
    links: Optional[Dict[str, Union[OASLink, Reference]]] = Field(
        None,
        description="A map of operations links that can be followed from the response.",
    )


class OASRequestBody(BaseModel):
    """Describes a single request body.

    Reference: OpenAPI 3.1
    """

    description: Optional[str] = Field(
        None, description="A brief description of the request body."
    )
    content: Dict[str, OASMediaType] = Field(
        description="The content of the request body."
    )
    required: bool = Field(
        False, description="Determines if the request body is required in the request."
    )


class OASOperation(BaseModel):
    """Describes a single API operation on a path.

    Reference: OpenAPI 2.0 (Swagger)
    """

    tags: Optional[List[str]] = Field(None, description="")
    summary: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    externalDocs: Optional[OASExternalDocument] = Field(
        None, description="Additional external documentation for this operation."
    )
    operationId: Optional[str] = Field(None, description="")
    consumes: Optional[List[str]] = Field(None, description="")
    produces: Optional[List[str]] = Field(None, description="")
    parameters: Optional[List[Union[Parameter, Reference]]] = Field(
        None, description=""
    )
    # TODO: this was done due to mypy reporting typing issue.
    responses: Optional[Dict[str, Union[OASResponse3, Reference]]] = Field(
        None, description=""
    )
    schemes: Optional[List[str]] = Field(None, description="")
    deprecated: bool = Field(False, description="")
    security: Optional[Dict[str, List[str]]] = Field(
        {},
        description="A declaration of which security schemes are applied for"
        " this operation",
    )

    class Config:
        extra = Extra.allow


class Path2(BaseModel):
    """Describes the operations available on a single path.

    Reference: OpenAPI 2.0 (Swagger)
    """

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


class OASOperation3(OASOperation):
    """Describes a single API operation on a path.

    Reference: OpenAPI 3.1
    """

    requestBody: Optional[Union[OASRequestBody, Reference]] = Field(
        None, description="The request body applicable for this operation"
    )
    callbacks: Optional[Dict[str, Dict[str, Union["Path3", Reference]]]] = Field(
        None,
        description="A map of possible out-of band callbacks related"
        " to the parent operation",
    )
    responses: Optional[Dict[str, Union[OASResponse3, Reference]]] = Field(
        None, description="A container for the expected responses of an operation."
    )
    servers: Optional[OASServer] = Field(
        None, description="An alternative server array to service this operation."
    )


class Path3(Path2):
    """Describes the operations available on a single path.

    Reference: OpenAPI 3.1
    """

    get: Optional[OASOperation3] = Field(None, description="")
    put: Optional[OASOperation3] = Field(None, description="")
    post: Optional[OASOperation3] = Field(None, description="")
    delete: Optional[OASOperation3] = Field(None, description="")
    options: Optional[OASOperation3] = Field(None, description="")
    head: Optional[OASOperation3] = Field(None, description="")
    patch: Optional[OASOperation3] = Field(None, description="")

    summary: Optional[str] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    trace: Optional[OASOperation3] = Field(None, description="")
    servers: Optional[List[OASServer]] = Field(None, description="")


# Handling Path3 <-> OASOperation3 circular dependency
OASOperation3.update_forward_refs()


class OASSecuritySchema(BaseModel):
    """Allows the definition of a security scheme that can be used by the operations.

    Reference: OpenAPI 2.0
    """

    type: Literal["basic", "apiKey", "oauth2"] = Field(
        description="The type of the security scheme."
    )
    description: Optional[str] = Field(
        None, description="A short description for security scheme."
    )
    name: str = Field(
        description="The name of the header or query parameter to be used."
    )
    oas_in: Literal["query", "header"] = Field(
        alias="in", description="The location of the API key."
    )
    flow: Literal["implicit", "password", "application", "accessCode"] = Field(
        description=" The flow used by the OAuth2 security scheme."
    )
    authorizationUrl: str = Field(
        description="The authorization URL to be used for this flow"
    )
    tokenUrl: str = Field(description="The token URL to be used for this flow")
    scopes: Dict[str, str] = Field(
        description="The available scopes for the OAuth2 security scheme"
    )


class OASOAuthFlow(BaseModel):
    """Configuration details for a supported OAuth Flow

    Reference: OpenAPI 3.1
    """

    authorizationUrl: str = Field(
        description="The authorization URL to be used for this flow."
    )
    tokenUrl: str = Field(description="The token URL to be used for this flow.")
    refreshUrl: Optional[str] = Field(
        None, description="The URL to be used for obtaining refresh tokens."
    )
    scopes: Dict[str, str] = Field(
        description="The available scopes for the OAuth2 security scheme."
    )


class OASOAuthFlows(BaseModel):
    """
    Allows configuration of the supported OAuth Flows.

    Reference: OpenAPI 3.1
    """

    implicit: Optional[OASOAuthFlow] = Field(
        None, description="Configuration for the OAuth Implicit flow."
    )
    password: Optional[OASOAuthFlow] = Field(
        None, description="Configuration for the OAuth Resource Owner Password flow."
    )
    clientCredentials: Optional[OASOAuthFlow] = Field(
        None, description="Configuration for the OAuth Client Credentials flow."
    )
    authorizationCode: Optional[OASOAuthFlow] = Field(
        None, description="Configuration for the OAuth Authorization Code flow."
    )


class OASSecuritySchema3(BaseModel):
    """Defines a security scheme that can be used by the operations.

    Reference: OpenAPI 3.1
    """

    type: Literal["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"] = Field(
        description="The type of the security scheme."
    )
    oas_in: Literal["query", "header", "cookie"] = Field(
        alias="in", description="The location of the API key."
    )
    scheme: str = Field(
        description="The name of the HTTP Authorization scheme"
        " to be used in the Authorization header as defined in [RFC7235]."
    )
    bearerFormat: Optional[str] = Field(
        description="A hint to the client to"
        " identify how the bearer token is formatted."
    )
    flows: OASOAuthFlows = Field(
        description="An object containing configuration"
        " information for the flow types supported."
    )
    openIdConnectUrl: str = Field(
        description="OpenId Connect URL to discover" " OAuth2 configuration values. "
    )


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
    responses: Optional[Dict[str, Union[OASResponse, Reference]]] = Field(
        None, description=""
    )
    securityDefinitions: Optional[Dict[str, OASSecuritySchema]] = Field(
        {},
        description="A declaration of the security schemes available"
        " to be used in the specification",
    )
    security: Optional[Dict[str, List[str]]] = Field(
        {},
        description="A declaration of which security schemes are applied"
        " for this operation",
    )
    tags: Optional[List[OASTag]] = Field(
        None,
        description="A list of tags used by the document with" " additional metadata",
    )
    externalDocs: Optional[OASExternalDocument] = Field(
        None, description="Additional external documentation"
    )

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


class OASComponents(BaseModel):
    """Holds a set of reusable objects for different aspects of the OAS.

    Reference: OpenAPI 3.1
    """

    schemas: Optional[Dict[str, OASSchema]] = Field(
        {}, description="An object to hold reusable Schema Objects."
    )
    responses: Optional[Dict[str, Union[OASResponse, Reference]]] = Field(
        {}, description="An object to hold reusable Response Objects."
    )
    parameters: Optional[Dict[str, Union[Parameter, Reference]]] = Field(
        {}, description="An object to hold reusable Parameter Objects."
    )
    examples: Optional[Dict[str, Union[OASExample, Reference]]] = Field(
        {}, description="An object to hold reusable Example Objects."
    )
    requestBodies: Optional[Dict[str, Union[OASRequestBody, Reference]]] = Field(
        {}, description="An object to hold reusable Request Body Objects."
    )
    headers: Optional[Dict[str, Union[Header, Reference]]] = Field(
        {}, description="An object to hold reusable Header Objects."
    )
    securitySchemas: Optional[Dict[str, Union[OASSecuritySchema3, Reference]]] = Field(
        {}, description="An object to hold reusable Security Scheme Objects."
    )
    links: Optional[Dict[str, Union[OASLink, Reference]]] = Field(
        {}, description="An object to hold reusable Callback Objects."
    )
    callbacks: Optional[
        Dict[str, Union[Dict[str, Union[Path3, Reference]], Reference]]
    ] = Field({}, description="An object to hold reusable Callback Objects.")
    pathItems: Optional[Dict[str, Union[Path3, Reference]]] = Field(
        {}, description="An object to hold reusable Path Item Objects."
    )


class OpenAPI3(BaseModel):
    """This is the root document object of the OpenAPI document.

    Reference: OpenAPI 3.1
    """

    info: Info = Field(description="Provides metadata about the API.")
    openapi: str = Field(
        description="This string MUST be the version number of the OpenAPI"
        " Specification that the OpenAPI document uses"
    )
    jsonSchemaDialect: Optional[AnyUrl] = Field(
        None,
        description="The default value for the $schema keyword within Schema"
        " Objects contained within this OAS document.",
    )
    servers: List[OASServer] = Field(
        [OASServer(url="/")],
        description="An array of Server Objects, which provide connectivity"
        " information to a target server.",
    )
    paths: Dict[str, Path3] = Field(
        description="The available paths and operations for the API."
    )
    webhooks: Optional[Dict[str, Union[Path3, Reference]]] = Field(
        {},
        description="The incoming webhooks that MAY be received as part of this"
        " API and that the API consumer MAY choose to implement.",
    )
    components: Optional[OASComponents] = Field(
        None, description="An element to hold various schemas for the specification."
    )
    security: Optional[Dict[str, List[str]]] = Field(
        {},
        description="A declaration of which security schemes are applied"
        " for this operation",
    )
    tags: Optional[List[OASTag]] = Field(
        None,
        description="A list of tags used by the document with" " additional metadata",
    )
    externalDocs: Optional[OASExternalDocument] = Field(
        None, description="Additional external documentation"
    )

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
