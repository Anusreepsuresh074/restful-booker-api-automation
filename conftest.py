import pytest
from dotenv import load_dotenv

from src.config.config_loader import get_config

# Load .env into the environment before any fixture reads a credential. `override=False` is the
# point: a variable already exported — a CI repository variable, or a one-off shell export for a
# single run — always wins over the file. In CI there is no .env at all and this is a no-op.
load_dotenv(override=False)


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        help="Environment to run against: dev | staging | prod",
    )


@pytest.fixture(scope="session")
def config(request):
    env = request.config.getoption("--env")
    return get_config(env)
