#!/usr/bin/env bash

coverage_percent=$(coverage report --format total)
echo "Test coverage: $coverage_percent%"
