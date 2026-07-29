import os
import sys
import socket
import webbrowser
import streamlit.web.cli as stcli

def find_free_port(start_port=8501):
    for port in range(start_port, start_port + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return 8501

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_script = os.path.join(base_dir, "app.py")
    
    port = find_free_port(8501)
    
    sys.argv = [
        "streamlit",
        "run",
        app_script,
        f"--server.port={port}",
        "--server.address=127.0.0.1",
        "--server.headless=true",
        "--global.developmentMode=false"
    ]
    
    webbrowser.open(f"http://127.0.0.1:{port}")
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()
