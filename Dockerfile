FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim
WORKDIR /app
COPY . /app

# create a clean environment from lockfile (preferred: use --locked)
RUN uv sync --locked --extra all

# run via the environment uv created (or use uv run)
CMD ["uv", "run", "--", "python", "-m", "square_database.main"]
