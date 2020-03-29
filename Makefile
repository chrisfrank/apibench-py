install:
	@python3 -m venv venv;
	@source venv/bin/activate && \
		pip install --upgrade pip setuptools wheel -r requirements.txt;

bench:
	@echo "\n\n*** BENCH SANS I/O ***\n"
	ab -c 50 -n 1000 -q 127.0.0.1:8000/hi
	@echo "\n\n*** BENCH HTTP I/O ***\n"
	ab -c 50 -n 1000 -q 127.0.0.1:8000/users
	@echo "\n\n*** BENCH DB I/O ***\n"
	ab -c 50 -n 1000 -q 127.0.0.1:8000/posts

flask:
	venv/bin/gunicorn --threads 40 bench_flask:app

starlette:
	venv/bin/gunicorn -k uvicorn.workers.UvicornWorker bench_starlette:app

go:
	go run bench_golang.go

.PHONY: bench install flask starlette go
