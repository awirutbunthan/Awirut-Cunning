import { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type DocumentResponse = { id: string; filename: string; status: string; fields: Record<string, string | null> };

export function App() {
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [message, setMessage] = useState("Choose a PDF, XLSX, or ZIP to begin review.");
  async function upload(file: File) {
    const body = new FormData(); body.append("file", file);
    const response = await fetch("http://localhost:8000/api/documents", { method: "POST", body });
    if (!response.ok) { setMessage(`Upload rejected: ${(await response.json()).detail}`); return; }
    const result: DocumentResponse = await response.json(); setDocument(result); setMessage("Uploaded. Verify extracted values before creating an audit.");
  }
  return <main><h1>Ledger Beacon</h1><p>Purchase-order and invoice review</p><label className="upload">Upload document<input aria-label="Upload document" type="file" accept=".pdf,.xlsx,.zip" onChange={(event) => { const file = event.target.files?.[0]; if (file) void upload(file); }} /></label><p role="status">{message}</p>{document && <section><h2>{document.filename}</h2><p>Status: {document.status}</p><dl>{Object.entries(document.fields).map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{value ?? "Not extracted — review required"}</dd></div>)}</dl></section>}</main>;
}
const root = document.getElementById("root");
if (root) createRoot(root).render(<App />);
