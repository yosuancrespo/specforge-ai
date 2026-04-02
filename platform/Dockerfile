FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SPECFORGE_REPO_ROOT=/workspace

WORKDIR /workspace/platform

RUN pip install --no-cache-dir uv

COPY platform/pyproject.toml /workspace/platform/pyproject.toml
COPY platform/README.md /workspace/platform/README.md
COPY platform/src /workspace/platform/src
RUN uv pip install --system -e /workspace/platform

COPY demo /workspace/demo
COPY evals /workspace/evals

EXPOSE 8000

CMD ["uvicorn", "specforge_ai.app:app", "--host", "0.0.0.0", "--port", "8000"]