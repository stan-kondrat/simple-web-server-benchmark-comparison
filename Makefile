
.NOTPARALLEL: run

all: clean build run 


# Clean

clean: clean-go clean-rust clean-c_libuv clean-results

clean-go:
	rm -f go/main

clean-rust:
	rm -rf rust/target

clean-c_libuv:
	rm -f rust/main

clean-results:
	rm -rf docs/results


# Build

build: build-go build-rust build-c_libuv

# Build - go
go/main: go/main.go
	cd go && go build
build-go: go/main

# Build - rust
rust/target/release/main: rust/src/main.rs
	cd rust && cargo build --release
build-rust: rust/target/release/main

# Build - c_libuv
c_libuv/main: c_libuv/main.c
	gcc -o c_libuv/main c_libuv/main.c -I/opt/homebrew/include -L/opt/homebrew/lib -luv && chmod +x c_libuv/main.c
build-c_libuv: c_libuv/main

# Run

run: run-bun run-go run-node run-php run-rust run-c_libuv system-info

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

run-rust: rust/target/release/main docs/results system-info
	./bench_runner.sh "rust" "./rust/target/release/main"

run-c_libuv: c_libuv/main docs/results system-info
	./bench_runner.sh "c_libuv" "./c_libuv/main"
	