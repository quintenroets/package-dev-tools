#!/usr/bin/env bash

# don't bump/check bump in GitHub actions
if [ "$GITHUB_ACTIONS" != "true" ]; then
    if ! git diff --staged pyproject.toml | grep -q version; then
        bump2version --config-file .bumpversion.cfg patch
    fi
fi
