from SpectrePDF.anonymizer import process_pdf

# Define targets from the redaction dict keys
import json
with open("redaction.json", "r") as f:
    redaction_dict = json.load(f)
target_words = list(redaction_dict.keys())

# Process the PDF (example: redact targets with replacement)
process_pdf(
    input_pdf="input.pdf",
    output_pdf="output_redacted.pdf",
    target_words=target_words,
    redaction_json_path="redaction.json",
    redact_targets=True,
    black_redaction=False,  # Set to True for black boxes without text
    dpi=500,
    tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Adjust path as needed
    verbosity=1
)
