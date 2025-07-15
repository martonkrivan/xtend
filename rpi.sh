#!/bin/bash

# Start backend
(cd backend && uv run uvicorn app.main:app --reload) &

# Start frontend
(cd frontend && bun dev) &

wait 