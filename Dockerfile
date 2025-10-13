# Use official slim python image (no platform hardcoded)
FROM python:3.12-slim AS base

# set working directory early to leverage caching
WORKDIR /app

# copy only requirements first for caching
COPY pyproject.toml setup.cfg /app/
# optional: if you have requirements.txt, copy that too

# install build dependencies first (isolated)
RUN pip install --upgrade pip setuptools wheel

# install dependencies (all extras)
RUN pip install .["all"]

# copy rest of the source code
COPY . /app

# final stage (can be same as base for simplicity)
FROM base AS final

# default command
CMD ["python3", "/usr/local/lib/python3.12/site-packages/square_database/main.py"]

# Uncomment for debugging
# CMD ["bash", "-c", "while true; do sleep 60; done"]
