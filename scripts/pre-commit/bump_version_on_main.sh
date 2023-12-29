#!/usr/bin/env bash

if [ "$(git branch --show-current)" = "main" ]; then
    scripts/pre-commit/bump_version.sh
fi
