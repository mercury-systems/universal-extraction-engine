.PHONY: install test test-all lint clean demo

install:
	pip install -e .

test:
	python3 -m pytest tests/ -v -m 'not integration'

test-all:
	python3 -m pytest tests/ -v

lint:
	python3 -m py_compile src/extraction_engine/*.py tests/*.py

clean:
	rm -rf __pycache__ .pytest_cache *.json *.csv src/*.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

demo:
	python3 -m extraction_engine.demo
