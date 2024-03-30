.PHONY: run
run:
	poetry run chainlit run src/app.py -w

.PHONY: secrets
secrets:
	fly secrets set $(shell tr '\n' ' ' < .env)

.PHONY: deploy
deploy: secrets
	fly deploy
