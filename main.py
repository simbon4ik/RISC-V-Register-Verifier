from dashboard.app import render
from src.api import run_test


def main():
    result = run_test(0x0000, 0x0020)
    print(result)


if __name__ == "__main__":
    main()
