FROM python:3.11-alpine

# Create folder and user
RUN adduser -D appuser && \
    mkdir /app && \
    chown appuser:appuser /app
WORKDIR /app
ENV PYTHONPATH=/app \
    PATH="/app:${PATH}:/home/appuser/.local/bin"
USER appuser

# Install poetry
RUN pip install --user poetry==1.8.2

# Install project dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-cache --only main

# Copy project files
COPY . .
RUN poetry install --only main

# Run the application
ENTRYPOINT poetry run chainlit run --host=0.0.0.0 --port=8000 -h noto_mate/lit.py
