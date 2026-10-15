from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def test_rejects_invalid_extension(client):
    response = client.post(
        "/api/documents", files={"file": ("danger.exe", b"x", "application/octet-stream")}
    )
    assert response.status_code == 422


def test_rejects_zip_traversal(client):
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("../escape.xlsx", b"content")
    response = client.post(
        "/api/documents", files={"file": ("unsafe.zip", output.getvalue(), "application/zip")}
    )
    assert response.status_code == 422
    assert "unsafe path" in response.json()["detail"]
