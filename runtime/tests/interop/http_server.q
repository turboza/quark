@version("1.2.3") // version is mandatory
package interop { // package interop is mandatory
    class Entrypoint { // class Entrypoint is mandatory
        void server(Runtime runtime, int port) { // runtime and port are mandatory constructor parameters
            runtime.serveHTTP("http://localhost:" + port.toString() + "/http_server", HelloServlet());

        }
        void client(Runtime runtime, int port) {

            TimeoutClient(runtime, port)
                .url("/http_server")
                .expectCode(200)
                .expectBody("Hello World!\r\n")
                .expectHeader("X-Custom-Header", "custom value")
                .check(0.5);
        }
    }
////include http_server.qinc
////include common.qinc
}