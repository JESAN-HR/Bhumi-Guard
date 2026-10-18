"""Generate clearly fictional, non-official exhibits for upload demonstrations."""

from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from backend.app.fixtures import scenarios
from backend.app.services import WATERMARK

ROOT = Path(__file__).resolve().parents[1]
for key in ("valid", "excess", "missing-history"):
    s = next(s for s in scenarios() if s["id"] == key)
    out = ROOT / "sample-documents" / f"DEMO-{key}.pdf"
    c = canvas.Canvas(str(out), pagesize=(595, 842))
    c.setTitle("DEMO - " + s["title"]["en"])
    c.setFillColor(HexColor("#153d4b"))
    c.rect(0, 720, 595, 122, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 24)
    c.drawString(42, 788, "BHUMIGUARD")
    c.setFont("Helvetica", 11)
    c.drawString(42, 761, "FICTIONAL TRANSACTION EXHIBIT / LANDTECH 2026")
    c.setFillColor(HexColor("#177d70"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(42, 681, s["title"]["en"])
    c.setFillColor(HexColor("#304b58"))
    c.setFont("Helvetica", 10)
    y = 650
    for line in (
        [
            "Sample exhibit, not an official deed or government document.",
            "Locations are real; parties, references, areas and dates are fictional.",
            "",
            "PROPOSED TRANSFER",
        ]
        + [f"{k}: {v}" for k, v in s["fields"].items()]
        + [
            "",
            "SUPPLIED HOLDING",
            f"Demo Seller A / DEMO-PARTY-A; holding: DEMO-HOLDING",
            f"Documented area: {s['holding']['area']} decimal / shotok",
            f"Relevant history complete: {s['holding']['history_complete']}",
            "Mutation: Demo Seller A, area 100 decimal / shotok.",
            "No previous transfers supplied in this sample.",
        ]
    ):
        for text in simpleSplit(line, "Helvetica", 10, 510):
            c.drawString(42, y, text)
            y -= 22
    c.setFillColor(HexColor("#fff3dc"))
    c.rect(30, 42, 535, 52, fill=1, stroke=0)
    c.setFillColor(HexColor("#79562a"))
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(297, 66, WATERMARK)
    c.save()
print("Generated 3 fictional PDF exhibits.")
