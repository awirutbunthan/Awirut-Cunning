from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


def test_rejects_invalid_extension(client):
    response = client.post(
        "/api/documents", files={"file": ("danger.exe", b"x", "application/octet-stream")}
    )
    assert response.status_code == 422


def test_rejects_content_type_spoofing(client):
    response = client.post(
        "/api/documents",
        files={"file": ("pretend.pdf", b"not a PDF", "application/pdf")},
    )
    assert response.status_code == 422
    assert "not a PDF" in response.json()["detail"]


def test_rejects_zip_traversal(client):
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("../escape.xlsx", b"content")
    response = client.post(
        "/api/documents", files={"file": ("unsafe.zip", output.getvalue(), "application/zip")}
    )
    assert response.status_code == 422
    assert "unsafe path" in response.json()["detail"]


def test_rejects_nested_zip(client):
    nested = BytesIO()
    with ZipFile(nested, "w", ZIP_DEFLATED) as archive:
        archive.writestr("inner.xlsx", b"not extracted")
    outer = BytesIO()
    with ZipFile(outer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("nested.zip", nested.getvalue())
    response = client.post(
        "/api/documents",
        files={"file": ("nested.zip", outer.getvalue(), "application/zip")},
    )
    assert response.status_code == 422
    assert "Nested ZIP" in response.json()["detail"]
