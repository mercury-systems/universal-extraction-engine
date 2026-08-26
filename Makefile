.PHONY: build run test clean install lint

build:
	docker compose build

run:
	docker compose up

test:
	python3 tests/test_extraction.py

clean:
	rm -rf __pycache__ .pytest_cache *.db output/*.json
	docker compose down --volumes --remove-orphans

install:
	pip install -r requirements.txt

lint:
	python3 -m py_compile src/main.py
	python3 -m py_compile src/scraper/*.py src/parser/*.py src/storage/*.py src/pipeline/*.py
