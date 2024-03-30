NotoMate
---

NotoMate is a chatbot-personal assistant with access to Notion.

# Getting started

## Prerequisites

1. [Poetry](https://python-poetry.org/) and [poetry dotenv plugin](https://pypi.org/project/poetry-plugin-dotenv/)
2. [API key for ChatGPT](https://platform.openai.com/api-keys)
3. API key for Notion: see [here](https://tsdaemon.github.io/education/2024/02/21/talk-notion-openai-functions.html#Secrets) how to set an app and get a key.

## Getting started

Install dependencies:
```
poetry install
```

Copy `sample.env` as `.env` and fill out with your configuration values:

```
cp sample.env .env
```

Run the app:

```
make run
```
