# CourierAI Convenience Automation Makefile

.PHONY: install run-dev run-api run-front test clean

install:
	pip install -r requirements.txt

run-api:
	python -m uvicorn main:app --host 0.0.0.0 --port 8000

run-dev1:
	python Backend/Backend_Dev1/main.py

run-front:
	python -m streamlit run Front-End/main.py

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
