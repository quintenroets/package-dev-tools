from typing import cast

from superpathlib import Path


def export_config() -> None:
    config_file = Path(".pre-commit-config.yaml")
    seed_file = Path(".pre-commit-seed.yaml")
    if seed_file.exists():
        hooks = cast("list[dict[str, str | bool]]", seed_file.yaml)
        defaults: dict[str, str | bool] = {
            "pass_filenames": False,
            "language": "system",
        }
        default_copies = {"id": "entry", "name": "id"}
        for hook in hooks:
            for k, v in defaults.items():
                hook.setdefault(k, v)
            for k, v in default_copies.items():
                hook.setdefault(k, hook[v])
        config_file.yaml = {"repos": [{"repo": "local", "hooks": hooks}]}
