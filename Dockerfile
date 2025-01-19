FROM --platform=linux/arm64/v8 arm64v8/python:3.12-slim

WORKDIR /app

ARG RELEASE_VERSION
RUN pip install square_database[all]==${RELEASE_VERSION}

CMD ["python3", "/usr/local/lib/python3.12/site-packages/square_database/main.py"]

# Uncomment for debugging
# CMD ["bash", "-c", "while true; do sleep 60; done"]
