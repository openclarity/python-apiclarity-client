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

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, IPvAnyAddress


class ApiType(str, Enum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


class DiffType(str, Enum):
    ZOMBIE_DIFF = "ZOMBIE_DIFF"
    SHADOW_DIFF = "SHADOW_DIFF"
    GENERAL_DIFF = "GENERAL_DIFF"
    NO_DIFF = "NO_DIFF"


class ApiInventorySortKey(str, Enum):
    NAME = "name"
    PORT = "port"
    HAS_RECONSTRUCTED_SPEC = "hasReconstructedSpec"
    HAS_PROVIDED_SPEC = "hasProvidedSpec"


class ApiEventSortKey(str, Enum):
    TIME = "time"
    METHOD = "method"
    PATH = "path"
    STATUS_CODE = "statusCode"
    SOURCE_IP = "sourceIP"
    DESTINATION_IP = "destinationIP"
    DESTINATION_PORT = "destinationPort"
    SPEC_DIFF_TYPE = "specDiffType"
    HOST_SPEC_NAME = "hostSpecName"
    API_TYPE = "apiType"


class HttpMethod(str, Enum):
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    CONNECT = "CONNECT"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    PATCH = "PATCH"


class HttpScheme(str, Enum):
    HTTP = "http"
    HTTPS = "https"


class AlertSeverityEnum(str, Enum):
    ALERT_INFO = "ALERT_INFO"
    ALERT_WARN = "ALERT_WARN"
    ALERT_CRITICAL = "ALERT_CRITICAL"


class SortDir(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


class ApiResponse(BaseModel):
    message: str = Field(
        description="An object that is return in all cases of failures."
    )


class ApiInfo(BaseModel):
    id: int = Field(description="")
    name: str = Field(description="API name")
    port: int = Field(description="")
    hasReconstructedSpec: bool = Field(description="")
    hasProvidedSpec: bool = Field(description="")


class ApiInfoWithType(ApiInfo):
    apiType: ApiType = Field(description="")


class ApiInventory(BaseModel):
    total: int = Field(
        description="Total filtered APIs count independent of pagination"
    )
    items: Optional[List[ApiInfo]] = Field(
        None,
        description="List of filtered APIs in the given page. List length must be "
        + "lower or equal to pageSize",
    )


class MethodAndPath(BaseModel):
    path: str = Field(description="")
    pathId: str = Field(description="")
    method: HttpMethod = Field(description="")


class SpecTag(BaseModel):
    description: str = Field(description="")
    name: str = Field(description="")
    methodAndPathList: List[MethodAndPath] = Field(description="")


class SpecInfo(BaseModel):
    tags: List[SpecTag] = Field(description="")


class OpenApiSpecs(BaseModel):
    providedSpec: SpecInfo = Field(description="")
    reconstructedSpec: SpecInfo = Field(description="")


class ApiEventPathAndMethods(BaseModel):
    path: str = Field(description="")
    methods: List[HttpMethod] = Field(description="")


class ReviewPathItem(BaseModel):
    suggestedPath: str = Field(
        description="Represents the parameterized path suggested by the engine"
    )
    apiEventsPaths: List[ApiEventPathAndMethods] = Field(
        description="Group of api event paths (original) that suggestedPath is "
        + "representing"
    )


class SuggestedReview(BaseModel):
    id: int = Field(description="")
    reviewPathItems: List[ReviewPathItem] = Field(
        description="The suggested path items"
    )


class ApprovedReview(BaseModel):
    reviewPathItems: List[ReviewPathItem] = Field(description="")


class ModuleAlert(BaseModel):
    moduleName: str = Field(description="Name of the module which created this alert")
    reason: str = Field(description="Optional description of reason of the alert")
    alert: AlertSeverityEnum = Field(description="")


class ApiEvent(BaseModel):
    id: int = Field(description="")
    requestTime: datetime = Field(description="")
    time: datetime = Field(description="")
    method: HttpMethod = Field(description="")
    path: str = Field(description="")
    query: str = Field(description="")
    statusCode: int = Field(description="")
    sourceIP: IPvAnyAddress = Field(description="")
    destinationIP: IPvAnyAddress = Field(description="")
    destinationPort: int = Field(description="")
    hasReconstructedSpecDiff: bool = Field(False, description="")
    hasProvidedSpecDiff: bool = Field(False, description="")
    specDiffType: DiffType = Field(description="")
    hostSpecName: str = Field(description="")
    apiInfoId: int = Field(description="hold the relevant api spec info id")
    apiType: ApiType = Field(description="")
    alerts: List[ModuleAlert] = Field(description="")


class ApiEventResponse(BaseModel):
    total: int = Field(
        description="Total events count in the given time range and " + "filters"
    )
    items: Optional[List[ApiEvent]] = Field(
        [],
        description="List of API events in the given time range, filters and page. "
        + "List length must be lower or equal to pageSize",
    )


class ApiEventSpecDiff(BaseModel):
    oldSpec: str = Field(description="Old spec json string")
    newSpec: str = Field(description="New spec json string")
    diffType: Optional[DiffType] = Field(description="")


class ApiUsage(BaseModel):
    numOfCalls: int = Field(description="")
    time: datetime = Field(description="")


class ApiUsages(BaseModel):
    existingApis: List[ApiUsage] = Field(description="")
    newApis: List[ApiUsage] = Field(description="")
    apisWithDiff: List[ApiUsage] = Field(description="")


class ApiCount(BaseModel):
    apiInfoId: int = Field(description="hold the relevant api info id")
    apiType: ApiType = Field(description="")
    numCalls: int = Field(description="")
    apiHostName: str = Field(description="")
    apiPort: int = Field(description="")


class SpecDiffTime(BaseModel):
    apiEventId: int = Field(description="")
    time: datetime = Field(description="")
    apiHostName: str = Field(description="")
    diffType: DiffType = Field(description="")


class HitCount(BaseModel):
    count: int = Field(description="")
    time: datetime = Field(description="")


class TelemetryHeader(BaseModel):
    key: str = Field(description="")
    value: str = Field(description="")


class TelemetryCommon(BaseModel):
    TruncatedBody: bool = Field(False, description="")
    # TODO: is body a byte[] in the API?
    body: str = Field(description="")
    headers: Optional[List[TelemetryHeader]] = Field(None, description="")
    # TODO: can we make this a datetime and use a JSON encoder to get a timestamp?
    time: int = Field(description="time since epoch in millis")
    version: Optional[str] = Field(None, description="")


class TelemetryRequest(BaseModel):
    common: TelemetryCommon
    host: str = Field(description="")
    method: HttpMethod = Field(HttpMethod.GET, description="")
    path: str = Field(description="")


class TelemetryResponse(BaseModel):
    common: TelemetryCommon
    statusCode: str = Field(description="")


class TelemetryTrace(BaseModel):
    destinationAddress: str = Field(description="host with optional port field")
    destinationNamespace: str
    request: TelemetryRequest = Field(description="")
    requestID: str
    response: TelemetryResponse = Field(description="")
    scheme: HttpScheme = Field(HttpScheme.HTTP, description="")
    sourceAddress: str = Field(description="URL host with optional port field")
