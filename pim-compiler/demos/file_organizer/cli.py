import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Organize files based on their type or other criteria.")

    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="The source directory to organize files from."
    )
    parser.add_argument(
        "--destination",
        type=str,
        required=True,
        help="The destination directory where organized files will be moved."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the file organization process without actually moving or creating files."
    )

    args = parser.parse_args()

    # Basic validation for directory existence (optional, can be done in core.py too)
    if not os.path.isdir(args.source):
        print(f"Error: Source directory '{args.source}' does not exist or is not a directory.")
        return

    if not os.path.isdir(args.destination):
        print(f"Error: Destination directory '{args.destination}' does not exist or is not a directory.")
        return

    print(f"Source Directory: {args.source}")
    print(f"Destination Directory: {args.destination}")
    print(f"Dry Run: {args.dry_run}")

    # Here you would call the core logic from core.py
    # For now, just print the arguments.
    print("CLI arguments parsed successfully. Core logic will be integrated here.")

if __name__ == "__main__":
    main()