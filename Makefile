
.NOTPARALLEL: run

all: clean build run 


# Clean

clean: clean-go clean-python clean-rust clean-c_libuv clean-zig clean-results

clean-go:
	rm -f go/main

clean-python:
	rm -rf python/.venv python/__pycache__

clean-rust:
	rm -rf rust/target

clean-c_libuv:
	rm -f rust/main

clean-zig:
	rm -rf zig/zig-cache zig/zig-out

clean-results:
	rm -rf docs/results


# Build

build: build-go build-python build-rust build-c_libuv build-zig

# Build - go
go/main: go/main.go
	cd go && go build
build-go: go/main

# Build - python
python/.venv/bin/gunicorn:
	cd python && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
build-python: python/.venv/bin/gunicorn

# Build - rust
rust/target/release/main: rust/src/main.rs
	cd rust && cargo build --release
build-rust: rust/target/release/main

# Build - c_libuv
c_libuv/main: c_libuv/main.c
	gcc -o c_libuv/main c_libuv/main.c -I/opt/homebrew/include -L/opt/homebrew/lib -luv && chmod +x c_libuv/main.c
build-c_libuv: c_libuv/main

# Build - zig
zig/zig-out/bin/main: zig/main.zig
	cd zig && mkdir -p zig-out/bin && zig build-exe main.zig -O ReleaseFast -femit-bin=zig-out/bin/main
build-zig: zig/zig-out/bin/main

# Run

run: run-bun run-go run-node run-php run-python run-rust run-c_libuv run-zig system-info

docs/results:
	mkdir -p docs/results

docs/results/system.json: docs/results
	source myenv/bin/activate && \
	echo "system_data = " > ./docs/results/system.json && \
	./system_info.py >> ./docs/results/system.json && \
	deactivate 
system-info: docs/results/system.json

run-bun: docs/results system-info
	./bench_runner.sh "bun" "bun ./bun/main.js"

run-go: go/main docs/results system-info
	./bench_runner.sh "go" "./go/main"

run-node: docs/results system-info
	./bench_runner.sh "node" "node ./node/main.js"

run-php: docs/results system-info
	./bench_runner.sh "php" "php -S 127.0.0.1:8080 ./php/main.php 2>/dev/null"

run-python: python/.venv/bin/gunicorn docs/results system-info
	./bench_runner.sh "python" "source python/.venv/bin/activate" "gunicorn --chdir python -w 4 -b 127.0.0.1:8080 main:app"

run-rust: rust/target/release/main docs/results system-info
	./bench_runner.sh "rust" "./rust/target/release/main"

run-c_libuv: c_libuv/main docs/results system-info
	./bench_runner.sh "c_libuv" "./c_libuv/main"

run-zig: zig/zig-out/bin/main docs/results system-info
	./bench_runner.sh "zig" "./zig/zig-out/bin/main"
