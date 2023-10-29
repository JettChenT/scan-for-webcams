"""
Scan For Webcams: Scan for webcams on the internet
"""
import sys

if __name__ == "__main__":
    if sys.version_info < (3, 6):
        print("Python version is too old. Please use Python 3.6 or higher.")
        sys.exit(1)

    import universal

    universal.Main()
