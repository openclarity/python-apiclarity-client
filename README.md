# Python APIClarity client

[![GitHub Actions status](https://github.com/openclarity/python-apiclarity-client/workflows/Test/badge.svg)](https://github.com/openclarity/python-apiclarity-client/actions)
[![Code style: Black](https://img.shields.io/badge/code%20style-Black-000000.svg)](https://github.com/psf/black)

Python client package for [APIClarity](https://github.com/openclarity/apiclarity) interaction.

[APIClarity](https://github.com/openclarity/apiclarity) is a modular tool that addresses several aspects of API Security, focusing specifically on [OpenAPI based APIs](https://spec.openapis.org/oas/latest.html). APIClarity approaches API Security in 2 different ways:

  * Captures all API traffic in a given environment and performs a set of security analysis to discover all potential security problems with detected APIs
  * Actively tests API endpoints to detect security issues in the implementation of such APIs.

## Usage

The `ClientSession` class is based on [requests.Session]() and can be used similarly. To configure the session, provide a `ClientSettings` object:

```python
from apiclarity import ClientSession, ClientSettings

apiclarity_session = ClientSession(ClientSettings(
    apiclarity_endpoint="http://apiclarity",
    default_timeout=(9.0, 3.0),
))
apiInfo = apiclarity_session.getInventory()
for api in apiInfo.items:
    print(f"received: {api}\n")
```

The settings can also be retrieved from the environment during creation of the `ClientSettings` object, given here with the defaults:

```shell
APICLARITY_ENDPOINT="http://apiclarity:8080"
TELEMETRY_ENDPOINT="http://apiclarity:9000"
HEALTH_ENDPOINT="http://apiclarity:8081"
```

# Contributing
Pull requests and bug reports are welcome. Please see [CONTRIBUTING.md](https://github.com/openclarity/python-apiclarity-client/blob/main/CONTRIBUTING.md).

# License
The code is released under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).
