FROM python:3.11-alpine

# Create folder
RUN mkdir /app
WORKDIR /app

# Install poetry
RUN pip install poetry==1.8.2

# Install project dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-cache --only main

# Copy project files
COPY . .
RUN poetry install --only main

# Run the application
ENTRYPOINT poetry run chainlit run src/app.py
