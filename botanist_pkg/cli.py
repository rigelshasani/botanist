import sys
import pathlib

# Make sure root is on path so we can import botanist.py
ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import botanist  # your original script

def main():
    botanist.main()  # assumes you added a main() wrapper in botanist.py
