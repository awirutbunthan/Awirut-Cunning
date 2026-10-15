from io import BytesIO

from openpyxl import Workbook


def spreadsheet(rows):
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def upload(client, name, payload):
    return client.post(
        "/api/documents",
        files={
            "file": (
                name,
                payload,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_upload_and_audit_discrepancy(client):
    po = upload(
        client,
        "po-synthetic.xlsx",
        spreadsheet(
            [
                ["Customer: Example Co Ltd"],
                ["Tax ID: 1234567890123"],
                ["Grand Total: 100.00"],
                ["Widget", 2, "50.00"],
            ]
        ),
    ).json()
    invoice = upload(
        client,
        "invoice-synthetic.xlsx",
        spreadsheet(
            [
                ["Customer: Example Company Limited"],
                ["Tax ID: 1234567890123"],
                ["Grand Total: 120.00"],
                ["Widget", 2, "60.00"],
            ]
        ),
    ).json()
    response = client.post(
        "/api/audits", json={"po_document_id": po["id"], "target_document_id": invoice["id"]}
    )
    assert response.status_code == 201
    audit = response.json()
    assert audit["status"] == "MANUAL_REVIEW"
    assert any(item["field"] == "grand_total" for item in audit["findings"])
    assert client.get(f"/api/audits/{audit['id']}/export.csv").status_code == 200


def test_missing_data_requires_manual_review(client):
    po = upload(
        client, "po.xlsx", spreadsheet([["Customer: Example Co"], ["Grand Total: 10.00"]])
    ).json()
    invoice = upload(client, "invoice.xlsx", spreadsheet([["Customer: Example Co"]])).json()
    audit = client.post(
        "/api/audits", json={"po_document_id": po["id"], "target_document_id": invoice["id"]}
    ).json()
    assert audit["status"] == "MANUAL_REVIEW"
    assert any(item["code"] == "MISSING_DATA" for item in audit["findings"])
