from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles

# Root directory for uploaded files
MEDIA_ROOT = Path("media")


async def save_upload(
    content: bytes,
    filename: str,
    subfolder: str = "",
) -> str:
    """Save *content* bytes to ``media/<subfolder>/<unique>_<filename>``.

    Returns the relative path string (e.g. ``"media/avatars/abc123_photo.jpg"``)
    that can be stored in the database or returned to the client.

    Args:
        content: Raw file bytes.
        filename: Original filename (used as suffix after a UUID prefix).
        subfolder: Optional sub-directory inside ``media/`` (e.g. ``"avatars"``).
    """
    dest_dir = MEDIA_ROOT / subfolder if subfolder else MEDIA_ROOT
    dest_dir.mkdir(parents=True, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}_{filename}"
    dest_path = dest_dir / unique_name

    async with aiofiles.open(dest_path, "wb") as f:
        await f.write(content)

    return str(dest_path).replace("\\", "/")


def delete_upload(relative_path: str) -> bool:
    """Delete the file at *relative_path*.

    Returns True if the file was deleted, False if it did not exist.
    """
    p = Path(relative_path)
    if p.exists():
        p.unlink()
        return True
    return False
