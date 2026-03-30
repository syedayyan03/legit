import subprocess
import time
import os
import sys

def run_project():
    print("Starting LEGIT Project...")
    
    # 1. Initialize Database
    print("\n[1/3] Initializing Database...")
    try:
        subprocess.run([sys.executable, "backend/database.py"], check=True)
        print("Database initialized successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing database: {e}")
        return

    # 2. Start Backend (show output directly in terminal for debugging)
    print("\n[2/3] Starting Backend Server (127.0.0.1:8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/main.py"],
    )

    # 3. Start Frontend
    print("\n[3/3] Starting Frontend Server (127.0.0.1:3000)...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000", "--bind", "127.0.0.1"],
        cwd=frontend_dir
    )

    print("\n" + "="*40)
    print("  PROJECT IS RUNNING!")
    print("  Backend: http://127.0.0.1:8000")
    print("  Frontend: http://127.0.0.1:3000")
    print("="*40)
    print("\nPress CTRL+C in this terminal to stop everything.")

    try:
        # Keep the script running while processes are alive
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print(f"Backend process stopped unexpectedly with code {backend_process.returncode}.")
                break
            if frontend_process.poll() is not None:
                print(f"Frontend process stopped unexpectedly with code {frontend_process.returncode}.")
                break
    except KeyboardInterrupt:
        print("\nStopping project...")
    finally:
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    run_project()
