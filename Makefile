.PHONY: run
run:
	poetry run chainlit run noto_mate/lit.py -w

.PHONY: run-docker
run-docker:
	docker build -t noto-mate .
	docker run -p 8000:8000 --env-file=.env.cloud noto-mate

.PHONY: secrets
secrets:
	fly secrets set $(shell tr '\n' ' ' < .env.cloud)

.PHONY: deploy
deploy: secrets
	fly deploy --ha=false
