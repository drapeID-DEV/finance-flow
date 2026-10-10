#!/bin/sh

set -e

exec uvicorn finance_flow.main:app --host 0.0.0.0 --port 8000