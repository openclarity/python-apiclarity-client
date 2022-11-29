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

import io
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from pydantic import AnyHttpUrl, BaseSettings, Field

from .schemas import (
    ApiCount,
    ApiEvent,
    ApiEventResponse,
    ApiEventSortKey,
    ApiEventSpecDiff,
    ApiInfoWithType,
    ApiInventory,
    ApiInventorySortKey,
    ApiType,
    ApiUsages,
    ApprovedReview,
    DiffType,
    HitCount,
    HttpMethod,
    OpenApiSpecs,
    SortDir,
    SpecDiffTime,
    SuggestedReview,
    TelemetryTrace,
)


class ClientSettings(BaseSettings):
    # TODO: take same env vars as Go client
    default_timeout: Union[float, Tuple[float, float]] = Field(
        11.0, description="Timeout (in secs) as value or (connect,read) tuple."
    )

    apiclarity_endpoint: Optional[AnyHttpUrl] = Field(
        AnyHttpUrl("http://apiclarity:8080"),
        description="APIClarity service API endpoint.",
    )
    telemetry_endpoint: Optional[AnyHttpUrl] = Field(
        AnyHttpUrl("http://apiclarity:9000"),
        description="APIClarity telemetry (trace) API endpoint.",
    )
    health_endpoint: Optional[AnyHttpUrl] = Field(
        AnyHttpUrl("http://apiclarity:8081"),
        description="APIClarity health API endpoint.",
    )

    class Config:
        case_sensitive = False
        # secrets_dir = "/run/secrets"


class ClientSession(requests.Session):
    def __init__(self, settings: Optional[ClientSettings] = None) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.settings = settings or ClientSettings()
        self.baseApi = "/api"

    def _validateAPISpec(self, specDict: Dict[str, Any]) -> None:
        openapi_version = specDict.get("openapi", "")
        if (
            "swagger" in specDict
            or openapi_version.startsWith("3.0")
            or openapi_version.startsWith("3.1")
        ):
            return
        else:
            raise Exception("unknown openapi version: " + str(openapi_version))

    def getInventory(
        self,
        *,
        apiType: ApiType = ApiType.EXTERNAL,
        apiInventorySortKey: ApiInventorySortKey = ApiInventorySortKey.NAME,
        page: int = 1,
        pageSize: int = 50,
        sortDir: Optional[SortDir] = None,
        apiNameIsFilter: List[str] = [],
        apiNameIsNotFilter: List[str] = [],
        apiNameStartsWithFilter: Optional[str] = None,
        apiNameEndsWithFilter: Optional[str] = None,
        apiNameContainsFilter: List[str] = [],
        portIsFilter: List[str] = [],
        portIsNotFilter: List[str] = [],
        hasProvidedSpecFilter: Optional[bool] = None,
        hasReconstructedSpecFilter: Optional[bool] = None,
        apiIdFilter: Optional[str] = None,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiInventory:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory"
        query_params: Dict[str, Union[bool, str, int, List[str]]] = {
            "type": apiType.value,
            "sortKey": apiInventorySortKey.value,
            "page": page,
            "pageSize": pageSize,
        }
        if sortDir is not None:
            query_params["sortDir"] = sortDir
        if apiNameIsFilter:
            query_params["apiNameIsFilter"] = apiNameIsFilter
        if apiNameIsNotFilter:
            query_params["apiNameIsNotFilter"] = apiNameIsNotFilter
        if apiNameStartsWithFilter:
            query_params["apiNameStartsWithFilter"] = apiNameStartsWithFilter
        if apiNameEndsWithFilter:
            query_params["apiNameEndsWithFilter"] = apiNameEndsWithFilter
        if apiNameContainsFilter:
            query_params["apiNameContainsFilter"] = apiNameContainsFilter
        if portIsFilter:
            query_params["portIsFilter"] = portIsFilter
        if portIsNotFilter:
            query_params["portIsNotFilter"] = portIsNotFilter
        if hasProvidedSpecFilter is not None:
            query_params["hasProvidedSpecFilter"] = hasProvidedSpecFilter
        if hasReconstructedSpecFilter is not None:
            query_params["hasReconstructedSpecFilter"] = hasReconstructedSpecFilter
        if apiIdFilter:
            query_params["apiIdFilter"] = apiIdFilter

        resp = self.get(
            url,
            params=query_params,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiInventory.parse_raw(resp.text)

    def postInventory(
        self,
        apiInfo: ApiInfoWithType,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> None:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory"
        resp = self.post(
            url,
            data=apiInfo.json(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()

    def getSpecs(
        self,
        apiId: str,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> OpenApiSpecs:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory"
            f"/{apiId}/specs"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return OpenApiSpecs.parse_raw(resp.text)

    def getProvidedSpec(
        self,
        apiId: str,
        validate: bool = False,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> Dict[str, Any]:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"provided_swagger.json"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        specDict = resp.json()
        if validate:
            self._validateAPISpec(specDict)
        return specDict

    def putProvidedSpec(
        self,
        apiId: str,
        apiSpec: Any,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> Optional[str]:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"specs/providedSpec"
        )
        if isinstance(apiSpec, io.IOBase):
            apiSpec = str(apiSpec.read())

        if isinstance(apiSpec, str):
            resp = self.put(
                url,
                json={"rawSpec": apiSpec},
                headers={
                    "Accept": "application/json",
                },
                timeout=(timeout if timeout else self.settings.default_timeout),
            )
        else:
            resp = self.put(
                url,
                json={"rawSpec": json.dumps(apiSpec)},
                headers={
                    "Accept": "application/json",
                },
                timeout=(timeout if timeout else self.settings.default_timeout),
            )
        # TODO: convert 400 status to spec validation failure exception
        resp.raise_for_status()
        apiSpec = resp.json()
        return apiSpec.get("rawSpec", None)

    def deleteProvidedSpec(
        self,
        apiId: str,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> None:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"specs/providedSpec"
        )
        resp = self.delete(
            url,
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()

    def getReconstructedSpec(
        self,
        apiId: str,
        validate: bool = False,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> Dict[str, Any]:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"reconstructed_swagger.json"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        specDict = resp.json()
        if validate:
            self._validateAPISpec(specDict)
        return specDict

    def deleteReconstructedSpec(
        self,
        apiId: str,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> None:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"specs/reconstructedSpec"
        )
        resp = self.delete(
            url,
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()

    def getSuggestedReview(
        self,
        apiId: str,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> SuggestedReview:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/{apiId}/"
            f"suggestedReview"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return SuggestedReview.parse_raw(resp.text)

    def postApprovedReview(
        self,
        reviewId: int,
        review: ApprovedReview,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> None:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiInventory/"
            f"{reviewId}/approvedReview"
        )
        resp = self.post(
            url,
            data=review.json(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()

    def getApiEvents(
        self,
        startTime: datetime,
        endTime: datetime,
        showNonApi: bool,
        *,
        page: int = 1,
        pageSize: int = 50,
        sortKey: ApiEventSortKey = ApiEventSortKey.HOST_SPEC_NAME,
        sortDir: Optional[SortDir] = None,
        methodIsFilter: List[HttpMethod] = [],
        pathIsFilter: List[str] = [],
        pathIsNotFilter: List[str] = [],
        pathStartsWithFilter: Optional[str] = None,
        pathEndsWithFilter: Optional[str] = None,
        pathContainsFilter: List[str] = [],
        statusCodeIsFilter: List[str] = [],
        statusCodeIsNotFilter: List[str] = [],
        statusCodeGteFilter: Optional[str] = None,
        statusCodeLteFilter: Optional[str] = None,
        sourceIPIsFilter: List[str] = [],
        sourceIPIsNotFilter: List[str] = [],
        destinationIPIsFilter: List[str] = [],
        destinationIPIsNotFilter: List[str] = [],
        destinationPortIsFilter: List[str] = [],
        destinationPortIsNotFilter: List[str] = [],
        hasSpecDiffFilter: Optional[bool] = None,
        specDiffTypeIsFilter: List[DiffType] = [],
        specIsFilter: List[str] = [],
        specIsNotFilter: List[str] = [],
        specStartsWithFilter: Optional[str] = None,
        specEndsWithFilter: Optional[str] = None,
        specContainsFilter: List[str] = [],
        alertIsFilter: List[str] = [],
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiEventResponse:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiEvents"
        query_params = {
            "startTime": startTime.isoformat(),
            "endTime": endTime.isoformat(),
            "showNonApi": showNonApi,
            "page": page,
            "pageSize": pageSize,
            "sortKey": sortKey.value,
        }
        if methodIsFilter:
            query_params["methodIsFilter"] = methodIsFilter
        if pathIsFilter:
            query_params["pathIsFilter"] = pathIsFilter
        if pathIsNotFilter:
            query_params["pathIsNotFilter"] = pathIsNotFilter
        if pathStartsWithFilter:
            query_params["pathStartsWithFilter"] = pathStartsWithFilter
        if pathEndsWithFilter:
            query_params["pathEndsWithFilter"] = pathEndsWithFilter
        if pathContainsFilter:
            query_params["pathContainsFilter"] = pathContainsFilter
        if statusCodeIsFilter:
            query_params["statusCodeIsFilter"] = statusCodeIsFilter
        if statusCodeIsNotFilter:
            query_params["statusCodeIsNotFilter"] = statusCodeIsNotFilter
        if statusCodeGteFilter:
            query_params["statusCodeGteFilter"] = statusCodeGteFilter
        if statusCodeLteFilter:
            query_params["statusCodeLteFilter"] = statusCodeLteFilter
        if sourceIPIsFilter:
            query_params["sourceIPIsFilter"] = sourceIPIsFilter
        if sourceIPIsNotFilter:
            query_params["sourceIPIsNotFilter"] = sourceIPIsNotFilter
        if destinationIPIsFilter:
            query_params["destinationIPIsFilter"] = destinationIPIsFilter
        if destinationIPIsNotFilter:
            query_params["destinationIPIsNotFilter"] = destinationIPIsNotFilter
        if destinationPortIsFilter:
            query_params["destinationPortIsFilter"] = destinationPortIsFilter
        if destinationPortIsNotFilter:
            query_params["destinationPortIsNotFilter"] = destinationPortIsNotFilter
        if hasSpecDiffFilter is not None:
            query_params["hasSpecDiffFilter"] = hasSpecDiffFilter
        if specDiffTypeIsFilter:
            query_params["specDiffTypeIsFilter"] = specDiffTypeIsFilter
        if specIsFilter:
            query_params["specIsFilter"] = specIsFilter
        if specIsNotFilter:
            query_params["specIsNotFilter"] = specIsNotFilter
        if specStartsWithFilter:
            query_params["specStartsWithFilter"] = specStartsWithFilter
        if specEndsWithFilter:
            query_params["specEndsWithFilter"] = specEndsWithFilter
        if specContainsFilter:
            query_params["specContainsFilter"] = specContainsFilter
        if alertIsFilter:
            query_params["alertIsFilter"] = alertIsFilter

        resp = self.get(
            url,
            params=query_params,  # type: ignore
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiEventResponse.parse_raw(resp.text)

    def getEvent(
        self,
        eventId: int,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiEvent:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiEvents/{eventId}"
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiEvent.parse_raw(resp.text)

    def getReconstructedSpecDiff(
        self,
        eventId: int,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiEventSpecDiff:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiEvents/{eventId}"
            f"/reconstructedSpecDiff"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiEventSpecDiff.parse_raw(resp.text)

    def getProvidedSpecDiff(
        self,
        eventId: int,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiEventSpecDiff:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiEvents/{eventId}"
            f"/providedSpecDiff"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiEventSpecDiff.parse_raw(resp.text)

    def getUsage(
        self,
        startTime: datetime,
        endTime: datetime,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> ApiUsages:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/dashboard/apiUsage"
        query_params = {
            "startTime": startTime.isoformat(),
            "endTime": endTime.isoformat(),
        }
        resp = self.get(
            url,
            params=query_params,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return ApiUsages.parse_raw(resp.text)

    def getMostUsed(
        self,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> List[ApiCount]:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/dashboard"
            f"/apiUsage/mostUsed"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return [ApiCount.parse_obj(obj) for obj in resp.json() if obj]

    def getLatestDiffs(
        self,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> List[SpecDiffTime]:
        url = (
            f"{self.settings.apiclarity_endpoint}{self.baseApi}/dashboard"
            f"/apiUsage/latestDiffs"
        )
        resp = self.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return [SpecDiffTime.parse_obj(obj) for obj in resp.json() if obj]

    def getHitCount(
        self,
        startTime: datetime,
        endTime: datetime,
        showNonApi: bool,
        *,
        methodIsFilter: List[HttpMethod] = [],
        providedPathIDIsFilter: List[str] = [],
        reconstructedPathIDIsFilter: List[str] = [],
        pathIsFilter: List[str] = [],
        pathIsNotFilter: List[str] = [],
        pathStartsWithFilter: Optional[str] = None,
        pathEndsWithFilter: Optional[str] = None,
        pathContainsFilter: List[str] = [],
        statusCodeIsFilter: List[str] = [],
        statusCodeIsNotFilter: List[str] = [],
        statusCodeGteFilter: Optional[str] = None,
        statusCodeLteFilter: Optional[str] = None,
        sourceIPIsFilter: List[str] = [],
        sourceIPIsNotFilter: List[str] = [],
        destinationIPIsFilter: List[str] = [],
        destinationIPIsNotFilter: List[str] = [],
        destinationPortIsFilter: List[str] = [],
        destinationPortIsNotFilter: List[str] = [],
        hasSpecDiffFilter: Optional[bool] = None,
        specDiffTypeIsFilter: List[DiffType] = [],
        specIsFilter: List[str] = [],
        specIsNotFilter: List[str] = [],
        specStartsWithFilter: Optional[str] = None,
        specEndsWithFilter: Optional[str] = None,
        specContainsFilter: List[str] = [],
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> List[HitCount]:
        url = f"{self.settings.apiclarity_endpoint}{self.baseApi}/apiUsage/hitCount"
        query_params = {
            "startTime": startTime.isoformat(),
            "endTime": endTime.isoformat(),
            "showNonApi": showNonApi,
        }
        if methodIsFilter:
            query_params["methodIsFilter"] = methodIsFilter
        if providedPathIDIsFilter:
            query_params["providedPathIDIsFilter"] = providedPathIDIsFilter
        if reconstructedPathIDIsFilter:
            query_params["reconstructedPathIDIsFilter"] = reconstructedPathIDIsFilter
        if pathIsFilter:
            query_params["pathIsFilter"] = pathIsFilter
        if pathIsNotFilter:
            query_params["pathIsNotFilter"] = pathIsNotFilter
        if pathStartsWithFilter:
            query_params["pathStartsWithFilter"] = pathStartsWithFilter
        if pathEndsWithFilter:
            query_params["pathEndsWithFilter"] = pathEndsWithFilter
        if pathContainsFilter:
            query_params["pathContainsFilter"] = pathContainsFilter
        if statusCodeIsFilter:
            query_params["statusCodeIsFilter"] = statusCodeIsFilter
        if statusCodeIsNotFilter:
            query_params["statusCodeIsNotFilter"] = statusCodeIsNotFilter
        if statusCodeGteFilter:
            query_params["statusCodeGteFilter"] = statusCodeGteFilter
        if statusCodeLteFilter:
            query_params["statusCodeLteFilter"] = statusCodeLteFilter
        if sourceIPIsFilter:
            query_params["sourceIPIsFilter"] = sourceIPIsFilter
        if sourceIPIsNotFilter:
            query_params["sourceIPIsNotFilter"] = sourceIPIsNotFilter
        if destinationIPIsFilter:
            query_params["destinationIPIsFilter"] = destinationIPIsFilter
        if destinationIPIsNotFilter:
            query_params["destinationIPIsNotFilter"] = destinationIPIsNotFilter
        if destinationPortIsFilter:
            query_params["destinationPortIsFilter"] = destinationPortIsFilter
        if destinationPortIsNotFilter:
            query_params["destinationPortIsNotFilter"] = destinationPortIsNotFilter
        if hasSpecDiffFilter is not None:
            query_params["hasSpecDiffFilter"] = hasSpecDiffFilter
        if specDiffTypeIsFilter:
            query_params["specDiffTypeIsFilter"] = specDiffTypeIsFilter
        if specIsFilter:
            query_params["specIsFilter"] = specIsFilter
        if specIsNotFilter:
            query_params["specIsNotFilter"] = specIsNotFilter
        if specStartsWithFilter:
            query_params["specStartsWithFilter"] = specStartsWithFilter
        if specEndsWithFilter:
            query_params["specEndsWithFilter"] = specEndsWithFilter
        if specContainsFilter:
            query_params["specContainsFilter"] = specContainsFilter

        resp = self.get(
            url,
            params=query_params,  # type: ignore
            headers={
                "Accept": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
        return [HitCount.parse_obj(obj) for obj in resp.json() if obj]

    def postTelemetry(
        self,
        telemetry: TelemetryTrace,
        timeout: Optional[Union[float, Tuple[float, float]]] = None,
    ) -> None:
        url = f"{self.settings.telemetry_endpoint}/api/telemetry"
        resp = self.post(
            url,
            data=telemetry.json(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=(timeout if timeout else self.settings.default_timeout),
        )
        resp.raise_for_status()
