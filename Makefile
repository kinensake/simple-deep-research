run:
	uvicorn --host 0.0.0.0 --port 8080 --reload --env-file .env main:app