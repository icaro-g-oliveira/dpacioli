import os
import subprocess
import sys
import webview
import threading

def start_llama_server():
    """Start the Llama server in a new console window."""
    try:
        subprocess.Popen(
            ['./llama/llama-server.exe', '-m', './models/gemma-3-4b-it-Q4_K_M.gguf'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Llama server started successfully.")
    except Exception as e:
        print(f"Error starting Llama server: {e}")
        sys.exit(1)

def start_npm_preview():
    """Run 'npm run preview' to start the preview server."""
    try:
        print("Starting npm run preview...")
        os.chdir("webui")
        subprocess.Popen(
            ['./node/node.exe', './node_modules/vite/bin/vite.js', 'preview'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("npm preview server started.")
    except Exception as e:
        print(f"Error starting npm preview: {e}")
        sys.exit(1)

def start_http_server_non_blocking():
    """Start the npm preview server in a non-blocking way."""
    npm_thread = threading.Thread(target=start_npm_preview)
    npm_thread.daemon = True  # Ensure the thread terminates when the main program ends
    npm_thread.start()
    print("npm preview server is running in the background.")

if __name__ == '__main__':
    start_llama_server()
    start_http_server_non_blocking()
    # Open a webview window pointing to the preview URL
    webview.create_window('dPacioli Junior', 'http://localhost:4173/', width=800, height=700, frameless=True)
    webview.start()

    input("Press Enter to continue...")  # Keeps the script running to maintain the processes.
