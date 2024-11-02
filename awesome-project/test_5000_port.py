import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Parse JSON data
        try:
            data = json.loads(post_data)
            print("Received data:", data)  # Log the data for testing
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())

if __name__ == "__main__":
    server_address = ('', 5000)  # Port 5000
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on port 5000...")
    httpd.serve_forever()
