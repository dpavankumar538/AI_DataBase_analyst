
from pathlib import Path
from uuid import uuid4

MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json", ".pdf"}


def save_uploaded_file(
    user_id: int,
    filename: str,
    content: bytes
) -> tuple[str, str]:
    """Save an uploaded file in the owner's private storage folder."""

    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user ID.")

    if not filename or not isinstance(filename, str):
        raise ValueError("Invalid filename.")

    if not isinstance(content, bytes) or not content:
        raise ValueError("Uploaded file is empty.")

    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError("File size exceeds the 16 MB limit.")

    # Normalize Windows and Unix path separators.
    safe_filename = Path(filename.replace("\\", "/")).name

    if not safe_filename:
        raise ValueError("Invalid filename.")

    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file extension.")

    # Generate a unique disk filename to avoid overwriting files.
    stored_filename = f"{uuid4().hex}{extension}"

    project_root = Path(__file__).resolve().parents[2]

    user_storage = (
        project_root / "storage" / "uploads" / f"user_{user_id}"
    )

    user_storage.mkdir(parents=True, exist_ok=True)

    file_path = user_storage / stored_filename

    try:
        with file_path.open("xb") as file:
            file.write(content)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    return str(file_path), safe_filename


def delete_stored_file(user_id: int, file_path: str) -> None:
    """Safely delete a file from the specified user's storage folder."""

    if type(user_id) is not int or user_id <= 0:
        raise ValueError("Invalid user ID.")

    if not file_path or not isinstance(file_path, str):
        raise ValueError("Invalid file path.")

    project_root = Path(__file__).resolve().parents[2]

    user_storage = (
        project_root / "storage" / "uploads" / f"user_{user_id}"
    ).resolve()

    candidate = Path(file_path)

    # Reject symbolic links.
    if candidate.is_symlink():
        raise ValueError("Symbolic links cannot be deleted.")

    path = candidate.resolve()

    # Ensure the file belongs directly to this user's folder.
    if path.parent != user_storage:
        raise ValueError("File does not belong to this user's storage.")

    # Do not delete directories.
    if path.exists():
        if not path.is_file():
            raise ValueError("Invalid file type.")

        path.unlink()