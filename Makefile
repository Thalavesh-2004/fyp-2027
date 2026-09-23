.PHONY: up down restart test baseline experiment clean help

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

test:
	pytest tests/ -v

baseline:
	python experiments/run_experiment.py --config config/baseline.yaml

clean:
	rm -rf output/* checkpoints/* data/raw/* data/processed/* data/ground_truth/*

help:
	@echo "Available commands:"
	@echo "  make up         - Start Docker Compose cluster"
	@echo "  make down       - Stop Docker Compose cluster"
	@echo "  make restart    - Restart Docker Compose cluster"
	@echo "  make test       - Run pytest unit and integration tests"
	@echo "  make baseline   - Run baseline experiment"
	@echo "  make clean      - Clean outputs and checkpoints"
