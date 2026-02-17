"""MediaAgent - Social Media AI Agent

Entry point for running the application.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.main import run

if __name__ == "__main__":
    run()
