from http.server import BaseHTTPRequestHandler, HTTPServer
from text_to_lineus import LineUs

class BasicServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(open("index.html","br").read())
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        print("recieved: ")
        print(self)
        try:
            body = self.rfile.read(content_len).decode()
            assert 0 < len(body) < 200
        except:
            self.send_error(code=400,message="Invalid input")
            return
        try:
            lineus = LineUs("192.168.1.212")
            lineus.write_msg(body)
        except:
            self.send_error(code=500,message="Unable to send message")
            return
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(b"ok")

server = HTTPServer(("192.168.1.202",9000), BasicServer)

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
