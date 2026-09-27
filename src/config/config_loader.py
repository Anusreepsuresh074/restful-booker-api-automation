import os
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


class ConfigLoader:
    """Single place every layer reads environment config through — never config.yaml directly."""

    def __init__(self, env: str):
        with open(_CONFIG_PATH, "r") as f:
            all_envs = yaml.safe_load(f)

        if env not in all_envs:
            raise ValueError(f"Unknown environment '{env}' — expected one of {list(all_envs.keys())}")

        self._env_config = all_envs[env]
        self.env = env

    @property
    def base_url(self) -> str:
        return os.environ.get("BASE_URL", self._env_config["base_url"])

    @property
    def timeout(self) -> int:
        return int(os.environ.get("TIMEOUT", self._env_config.get("timeout", 30)))


def get_config(env: str) -> ConfigLoader:
    return ConfigLoader(env)
