FROM node:24-bookworm-slim AS frontend
WORKDIR /app/frontend
RUN corepack enable && corepack prepare pnpm@11.25.0 --activate
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.lock backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend/ backend/
COPY data/ data/
COPY sample-documents/ sample-documents/
COPY --from=frontend /app/frontend/dist frontend/dist
RUN useradd --create-home app && mkdir runtime && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["sh", "-c", "python -m alembic -c backend/alembic.ini upgrade head && python -m backend.app.seed && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
