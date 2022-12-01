# Contributing
Pull requests and bug reports are welcome.

For larger changes please create an Issue in GitHub first to discuss your proposed changes and possible implications.

## Set up your development environment

This repo uses both [Poetry](https://python-poetry.org/) and [pre-commit](https://pre-commit.com/) to manage dependencies, code-formatting, etc. You will need to install them first. Refer to the sites for installation instructions for your platform.

```sh
    $ poetry config virtualenvs.in-project true # install venv in local project directory for IDE support
    $ poetry install  # install main and dev dependencies for testing, etc.
    $ pre-commit install  # install pre-commit packages for linting, formatting, etc.
```

## Testing

To run local and unit tests, you will need to have [Docker](https://www.docker.com/products/docker-desktop/) installed locally because the testing framework uses the [pytest-docker-tools](https://github.com/Jc2k/pytest-docker-tools) package.

Use poetry to install the dependencies in a local virtual environment, then run pytest from the top-level:

```sh
    $ poetry install
    $ poetry run pytest -W error::UserWarning
```

If you want the test framework to leave the containers running to read logs or inspect the containers or what have you, you can use the following command:

```sh
    $ poetry run pytest --reuse-containers
```

After that, the script in `scripts/docker_tools_cleanup.sh` will remove the containers, volumes, and networks used in the tests.
