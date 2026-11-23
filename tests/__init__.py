import sys
from pathlib import Path

# Make `src/` importable so tests can do `from sales import ...`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
