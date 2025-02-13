
const server = Bun.serve({
    port: 8080,
    fetch(request) {
      return new Response("Welcome to Bun!");
    },
});
  
console.log(`Listening on ${server.url}`);