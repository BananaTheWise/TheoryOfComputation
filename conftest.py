# conftest.py  ← place at project ROOT, not inside tests/
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))