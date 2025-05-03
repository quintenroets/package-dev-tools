from typing import Any, cast

from superpathlib import Path


def export_config() -> None:
    config_file = Path(".pre-commit-config.yaml")
    seed_file = Path(".pre-commit-seed.yaml")
    if seed_file.exists():
        config = cast("dict[str, list[dict[str, list[Any]]]]", seed_file.yaml)
        hooks = cast("list[dict[str, str]]", config["repos"][0]["hooks"])
        for hook in hooks:
            if "language" not in hook:
                hook["language"] = "system"
            if "id" not in hook:
                hook["id"] = hook["entry"]
            if "name" not in hook:
                hook["name"] = hook["id"]
        config_file.yaml = config
