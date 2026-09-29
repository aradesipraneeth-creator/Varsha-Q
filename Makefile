.PHONY: install test train demo run-backend run-frontend clean docker-up docker-down

install:
	pip install -r requirements.txt
	cd frontend && npm install

test:
	python -m pytest tests/

train:
	python scripts/train_all.py

demo:
	python scripts/run_demo.py

run-backend:
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build

docker-down:
	docker compose down
