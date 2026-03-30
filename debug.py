
import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Virtual Environment: {'Yes' if hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix) else 'No'}")

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    print("\nTesting imports...")
    import main
    import scraper
    import auth
    import predictor
    import database
    print("All imports successful!")
except Exception as e:
    print(f"\nError during import: {e}")
    import traceback
    traceback.print_exc()
