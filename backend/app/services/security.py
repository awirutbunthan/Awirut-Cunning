from io import BytesIO
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".xlsx", ".zip"}
MIME_BY_EXTENSION = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    },
    ".zip": {"application/zip", "application/x-zip-compressed", "application/octet-stream"},
}


def reject(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def validate_upload(filename: str, content_type: str | None, data: bytes) -> str:
    extension = PurePosixPath(filename).suffix.lower()
    if not filename or extension not in ALLOWED_EXTENSIONS:
        reject("Unsupported file extension")
    if content_type and content_type not in MIME_BY_EXTENSION[extension]:
        reject("Content type does not match file extension")
    if not data:
        reject("Empty upload")
    if len(data) > settings.max_upload_bytes:
        reject("Upload exceeds size limit")
    if extension == ".zip":
        validate_zip(data)
    return extension


def validate_zip(data: bytes) -> None:
    try:
        with ZipFile(BytesIO(data)) as archive:
            infos = archive.infolist()
            if len(infos) > settings.max_zip_entries:
                reject("ZIP contains too many entries")
            total = 0
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                    reject("ZIP contains an unsafe path")
                if info.is_dir():
                    continue
                if info.external_attr >> 16 & 0o170000 == 0o120000:
                    reject("ZIP contains a symlink")
                total += info.file_size
                if total > settings.max_zip_uncompressed_bytes:
                    reject("ZIP extracted size exceeds limit")
                if (
                    info.compress_size
                    and info.file_size / info.compress_size > settings.max_zip_ratio
                ):
                    reject("ZIP compression ratio exceeds limit")
    except BadZipFile:
        reject("Invalid ZIP archive")
