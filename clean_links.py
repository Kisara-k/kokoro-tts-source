import fitz  # PyMuPDF
import os

# Define phrases to redact
PHRASES_TO_REDACT = [
    "OceanofPDF.com",
    "https://oceanofpdf.com/",
    "http://www.profilebooks.com/"
]

# Process all PDFs in the current directory
for filename in os.listdir():
    if filename.lower().endswith(".pdf"):
        print(f"Processing: {filename}")
        doc = fitz.open(filename)
        for page in doc:
            for phrase in PHRASES_TO_REDACT:
                for inst in page.search_for(phrase):
                    page.add_redact_annot(inst, fill=(1, 1, 1))
            page.apply_redactions()
        output_path = f"redacted_{filename}"
        doc.save(output_path)
        doc.close()
        print(f"Saved redacted PDF to: {output_path}")

print("All files redacted and saved.")
