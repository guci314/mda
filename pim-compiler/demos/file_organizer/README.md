# File Organizer

A simple command-line utility to organize files into subdirectories based on their file extensions.

## Features

*   Organize files from a source directory into a destination directory.
*   Creates subdirectories named after file extensions (e.g., `images`, `documents`, `videos`).
*   Supports a dry-run mode to preview changes without actually moving files.
*   Handles existing files by skipping or overwriting (future feature/configurable).

## Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/your-username/file-organizer.git
    cd file-organizer
    ```

2.  **Install using pip:**
    ```bash
    pip install .
    ```
    This will install the `file-organizer` package and make the `organize` command available in your terminal.

## Usage

The `file-organizer` tool can be run from your command line.

### Basic Usage

To organize files from a source directory to a destination directory: