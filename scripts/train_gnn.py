import sys
from pathlib import Path

# Add scripts directory to path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent))

from train_lnn import train_spatiotemporal

if __name__ == "__main__":
    train_spatiotemporal()
