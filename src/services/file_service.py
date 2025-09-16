"""File handling services"""

import base64
import hashlib
from pathlib import Path
from config import CACHE_DIR


def get_cached_file_path(contents, filename):
    """Generate a cached file path based on filename and content hash"""
    # Decode the uploaded file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    # Create hash of file content for uniqueness
    content_hash = hashlib.md5(decoded).hexdigest()[:8]

    # Clean filename (remove special characters, keep extension)
    clean_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
    name_without_ext = Path(clean_filename).stem
    ext = Path(clean_filename).suffix

    # Create cached filename: originalname_hash.pdf
    cached_filename = f"{name_without_ext}_{content_hash}{ext}"
    cached_file_path = CACHE_DIR / cached_filename

    # Write file if it doesn't exist
    if not cached_file_path.exists():
        cached_file_path.write_bytes(decoded)

    return str(cached_file_path)


def get_sample_filepath(contract_filename):
    """Get the file path for a sample contract"""
    try:
        # Get the directory where this script is located
        script_dir = Path(__file__).parent.parent

        # Look for the file in the data directory
        file_path = script_dir / "data" / contract_filename
        if file_path.exists():
            return str(file_path)

        # If file not found, return None
        raise FileNotFoundError(f"Sample contract {contract_filename} not found")
    except Exception as e:
        print(f"Error loading sample contract {contract_filename}: {e}")
        return None
