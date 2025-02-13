package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet && r.URL.Path == "/" {
		fmt.Fprintln(w, "Hello, World!")
		return
	}
	http.NotFound(w, r)
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("Server is running on port 8080...")
	http.ListenAndServe("127.0.0.1:8080", nil)
}
