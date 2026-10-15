from pydantic import BaseModel


class Settings(BaseModel):
    max_upload_bytes: int = 10 * 1024 * 1024
    max_files_per_request: int = 5
    max_zip_entries: int = 100
    max_zip_uncompressed_bytes: int = 20 * 1024 * 1024
    max_zip_ratio: int = 100


settings = Settings()
