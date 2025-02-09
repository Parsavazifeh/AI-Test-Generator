import os
import subprocess
from pathlib import Path

def track_generated_tests():
    """Automatically add, commit, and push generated test cases."""
    test_dir = Path("tests/unit")
    if not test_dir.exists():
        print("❌ Test directory does not exist. Skipping Git commit.")
        return
    
    # Run git commands
    subprocess.run(["git", "add", str(test_dir)], check=False)
    subprocess.run(["git", "commit", "-m", "🔍 Auto-generated test cases"], check=False)
    subprocess.run(["git", "push"], check=False)

if __name__ == "__main__":
    track_generated_tests()