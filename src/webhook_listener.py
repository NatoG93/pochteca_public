#!/usr/bin/env python3
import http.server
import socketserver
import subprocess
import json
import os

PORT = 5001
SCRIPT_TO_RUN = "./updatedata.sh"

class WebhookHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/update':
            try:
                # Parse JSON body if present
                content_length = int(self.headers.get('Content-Length', 0))
                args = []
                
                if content_length > 0:
                    body = self.rfile.read(content_length)
                    data = json.loads(body)
                    print(f"Received payload: {data}")
                    
                    # specific keys to flags mapping
                    if 'days' in data:
                        args.extend(['--days', str(data['days'])])
                    if 'timerange' in data:
                        args.extend(['--timerange', str(data['timerange'])])
                    if 'timeframes' in data:
                        # Handle list or string
                        tf = data['timeframes']
                        args.append('--timeframes')
                        if isinstance(tf, list):
                            args.extend(tf)
                        else:
                            args.extend(tf.split())
                    if 'pairs' in data:
                        pairs = data['pairs']
                        args.append('--pairs')
                        if isinstance(pairs, list):
                            args.extend(pairs)
                        else:
                            args.extend(pairs.split())
                
                # Construct command
                cmd = [SCRIPT_TO_RUN] + args
                print(f"Executing: {' '.join(cmd)}")
                
                # Check if script exists
                if not os.path.exists(SCRIPT_TO_RUN):
                    self._send_response(500, {"status": "error", "message": f"Script {SCRIPT_TO_RUN} not found"})
                    return

                # Execute the script
                result = subprocess.run(
                    cmd, 
                    check=True, 
                    capture_output=True, 
                    text=True
                )
                
                print("Update completed successfully.")
                self._send_response(200, {
                    "status": "success", 
                    "message": "Update executed", 
                    "args_used": args,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                })
                
            except json.JSONDecodeError:
                 self._send_response(400, {"status": "error", "message": "Invalid JSON"})
            except subprocess.CalledProcessError as e:
                print(f"Error executing script: {e}")
                self._send_response(500, {
                    "status": "error", 
                    "message": "Script execution failed", 
                    "stdout": e.stdout,
                    "stderr": e.stderr
                })
            except Exception as e:
                print(f"Unexpected error: {e}")
                self._send_response(500, {"status": "error", "message": str(e)})
        else:
            self._send_response(404, {"status": "error", "message": "Not Found"})

    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server():
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        print(f"Serving n8n webhook listener on port {PORT}")
        print(f"POST to http://localhost:{PORT}/update to trigger {SCRIPT_TO_RUN}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
