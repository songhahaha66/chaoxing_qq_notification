#!/bin/bash

uv run main.py &
uv run uvicorn api:app --host 0.0.0.0 --port 8000 &

