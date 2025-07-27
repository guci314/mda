import os

def get_file_extension(filename):
    """
    Extracts the file extension from a given filename.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The file extension (e.g., "txt", "jpg"), or an empty string if no extension.
    """
    return os.path.splitext(filename)[1].lstrip('.').lower()

def create_directory_if_not_exists(directory_path):
    """
    Creates a directory if it does not already exist.

    Args:
        directory_path (str): The path of the directory to create.
    """
    os.makedirs(directory_path, exist_ok=True)

def get_category_from_extension(extension):
    """
    Maps a file extension to a predefined category.

    Args:
        extension (str): The file extension (e.g., "txt", "jpg").

    Returns:
        str: The category name (e.g., "Documents", "Images"), or "Others" if no specific category.
    """
    extension_to_category = {
        # Documents
        'txt': 'Documents', 'pdf': 'Documents', 'doc': 'Documents', 'docx': 'Documents',
        'xls': 'Documents', 'xlsx': 'Documents', 'ppt': 'Documents', 'pptx': 'Documents',
        'odt': 'Documents', 'ods': 'Documents', 'odp': 'Documents',

        # Images
        'jpg': 'Images', 'jpeg': 'Images', 'png': 'Images', 'gif': 'Images',
        'bmp': 'Images', 'tiff': 'Images', 'webp': 'Images', 'svg': 'Images',

        # Videos
        'mp4': 'Videos', 'mkv': 'Videos', 'avi': 'Videos', 'mov': 'Videos',
        'wmv': 'Videos', 'flv': 'Videos', 'webm': 'Videos',

        # Audio
        'mp3': 'Audio', 'wav': 'Audio', 'aac': 'Audio', 'flac': 'Audio',
        'ogg': 'Audio', 'wma': 'Audio',

        # Archives
        'zip': 'Archives', 'rar': 'Archives', '7z': 'Archives', 'tar': 'Archives',
        'gz': 'Archives', 'bz2': 'Archives', 'xz': 'Archives',

        # Executables
        'exe': 'Executables', 'msi': 'Executables', 'dmg': 'Executables', 'app': 'Executables',

        # Code
        'py': 'Code', 'js': 'Code', 'html': 'Code', 'css': 'Code', 'java': 'Code',
        'c': 'Code', 'cpp': 'Code', 'h': 'Code', 'hpp': 'Code', 'json': 'Code',
        'xml': 'Code', 'sh': 'Code', 'bat': 'Code', 'md': 'Code', 'yml': 'Code',
        'yaml': 'Code', 'go': 'Code', 'rb': 'Code', 'php': 'Code', 'ts': 'Code',
        'tsx': 'Code', 'jsx': 'Code', 'vue': 'Code', 'swift': 'Code', 'kt': 'Code',
        'rs': 'Code', 'sql': 'Code', 'csv': 'Code',

        # Spreadsheets (already covered by Documents, but good to be explicit if needed)
        'csv': 'Documents',

        # Fonts
        'ttf': 'Fonts', 'otf': 'Fonts', 'woff': 'Fonts', 'woff2': 'Fonts',

    }
    return extension_to_category.get(extension, 'Others')