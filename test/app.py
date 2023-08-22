from http.server import SimpleHTTPRequestHandler, HTTPServer

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello, World!")

def run():
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, MyHandler)
    print('Running server...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
