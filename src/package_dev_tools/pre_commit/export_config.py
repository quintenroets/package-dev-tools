from typing import Any, cast

from superpathlib import Path


def export_config() -> None:
    config_file = Path(".pre-commit-config.yaml")
    seed_file = Path(".pre-commit-seed.yaml")
    if seed_file.exists():
        hooks = cast("list[dict[str, str]]", seed_file.yaml)
        defaults = {"pass_filenames": False, "language": "system"}
        default_copies = {"id": "entry", "name": "id"}
        for hook in hooks:
            for k, v in defaults.items():
                if k not in hook:
                    hook[k] = v
            for k, v in default_copies.items():
                if k not in hook:
                    hook[k] = hook[v]
        config_file.yaml = {"repos": [{"repo": "local", "hooks": hooks}]}
