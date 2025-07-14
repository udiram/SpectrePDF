# SpectrePDF: Advanced PDF Redaction and Annotation Tool

![SpectrePDF Logo](https://via.placeholder.com/150?text=SpectrePDF) <!-- Replace with actual logo if available -->

Welcome to **SpectrePDF**, a powerful Python library designed for detecting, annotating, and redacting sensitive information in PDF documents using OCR (Optical Character Recognition). Whether you're handling confidential reports, legal documents, or personal files, SpectrePDF makes it easy to identify specific words or phrases and either highlight them with boxes or redact them securely—replacing them with custom text or blacking them out entirely.

Built with efficiency and accuracy in mind, SpectrePDF leverages high-resolution rendering and intelligent word grouping to ensure precise results, even on complex layouts. It's ideal for privacy compliance (e.g., GDPR, HIPAA), data anonymization, or simply reviewing PDFs for key terms.

## Why Choose SpectrePDF?
- **Accurate OCR Detection**: Uses Tesseract OCR to scan rendered PDF pages at customizable DPI for reliable word recognition.
- **Flexible Redaction Options**: Redact with custom replacement text, black boxes, or just draw outlines for review.
- **Smart Grouping**: Automatically groups words into lines and merges adjacent targets for clean, professional results.
- **High Performance**: Processes multi-page PDFs with progress tracking via `tqdm`.
- **Open-Source and Extensible**: Easy to integrate into your workflows, with verbose logging for debugging.

SpectrePDF is perfect for developers, data privacy officers, researchers, and anyone needing robust PDF manipulation tools.

## Features
- **Word Detection**: Scan PDFs for specific target words or phrases using OCR.
- **Box Annotation**:
  - Draw colored outlines around detected words (blue for targets, red for others).
  - Option to show boxes around all words or only targets.
- **Redaction Modes**:
  - Replace targets with custom text from a JSON dictionary (e.g., anonymize names like "John Doe" to "[REDACTED]").
  - Blackout targets completely for irreversible redaction.
  - Whiteout and overlay replacement text with auto-scaled font sizing.
- **Customization**:
  - Adjustable DPI for rendering (higher for better accuracy, e.g., 500 DPI).
  - Verbosity levels for silent, basic, or detailed output.
  - Support for custom Tesseract executable path.
- **Efficiency Tools**: Progress bars, timing metrics, and error handling for seamless processing.
- **Output**: Generates a new PDF with modifications, preserving original layout.

## Installation
SpectrePDF is a Python package that requires Python 3.6+. Install it via pip (assuming you've packaged it; if not, clone the repo and install dependencies manually).

```bash
pip install spectrepdf  # If published on PyPI; otherwise, use git
# Or clone and install:
git clone https://github.com/udiram/spectrePDF.git
cd spectrePDF
pip install -r requirements.txt
```

### Dependencies
SpectrePDF relies on the following libraries (install via `pip`):
- `pymupdf` (PyMuPDF for PDF handling)
- `Pillow` (PIL for image manipulation)
- `pytesseract` (Tesseract OCR wrapper)
- `img2pdf` (Image to PDF conversion)
- `tqdm` (Progress bars)
- `statistics` (Standard library, for median calculations)

Additionally, install Tesseract OCR on your system:
- Windows: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.
- macOS: `brew install tesseract`
- Linux: `sudo apt install tesseract-ocr`

No internet access is required during runtime—everything runs locally.

## Quick Start
1. **Prepare Your Redaction Dictionary**: Create a `redaction.json` file mapping target words to replacements. Example:
   ```json
   {
       "confidential": "[REDACTED]",
       "secret": "[CLASSIFIED]",
       "john doe": "[ANONYMIZED]"
   }
   ```
   Keys are case-insensitive during detection.

2. **Run the Processor**: Use the `process_pdf` function from `SpectrePDF.anonymizer`.

   Here's a basic example script:

   ```python
   from SpectrePDF.anonymizer import process_pdf
   import json

   # Load targets from redaction dict keys
   with open("redaction.json", "r") as f:
       redaction_dict = json.load(f)
   target_words = list(redaction_dict.keys())

   # Process the PDF (redact with replacements)
   process_pdf(
       input_pdf="input.pdf",
       output_pdf="output_redacted.pdf",
       target_words=target_words,
       redaction_json_path="redaction.json",
       redact_targets=True,
       black_redaction=False,  # False for text replacement; True for black boxes
       dpi=500,
       tesseract_cmd="/usr/local/bin/tesseract",  # Adjust to your Tesseract path
       verbosity=1  # 0: silent, 1: progress, 2: detailed
   )
   ```

   This will scan `input.pdf` for words like "confidential" or "john doe", redact them with replacements from the JSON, and save the result as `output_redacted.pdf`.

## Understanding the `process_pdf` Function

The `process_pdf` function is the core entry point of the SpectrePDF library. It enables users to load a PDF document, perform OCR-based detection of specific words or phrases, and then either annotate the document by drawing boxes around detected elements or redact sensitive information. The process involves rendering PDF pages as high-resolution images, running OCR to extract text data, grouping words logically, and applying modifications before saving a new PDF.

This function is highly configurable, allowing for various modes of operation such as simple detection with annotations, targeted redaction with replacements, or secure blackouts. Below, I'll break down its purpose, workflow, and every parameter in detail to ensure you can use it effectively. All parameters are designed to balance flexibility, accuracy, and performance.

#### Function Signature and Overview
```python
def process_pdf(
    input_pdf: str,
    output_pdf: str,
    target_words: list,
    redaction_json_path: str,
    show_all_boxes: bool = False,
    only_target_boxes: bool = False,
    redact_targets: bool = False,
    black_redaction: bool = False,
    tesseract_cmd: str = None,
    dpi: int = 500,
    verbosity: int = 1
):
    """
    Process a PDF to detect, optionally draw boxes around, or redact and replace specific target words using OCR.
    """
```
- **Core Workflow**:
  1. Open the input PDF using PyMuPDF.
  2. Render each page as an image at the specified DPI.
  3. Perform OCR on each image using Tesseract to extract words, positions, and bounding boxes.
  4. Collect and group words into lines based on vertical alignment.
  5. Identify target words (case-insensitive partial matches) and merge adjacent targets if needed.
  6. Depending on parameters, either draw boxes for annotation or apply redaction.
  7. Convert modified images back to a PDF and save it.
  8. Handle errors gracefully (e.g., file not found, invalid JSON) and provide timing metrics.

The function raises exceptions for invalid inputs (e.g., non-list `target_words`, missing files) to prevent silent failures. It supports multi-page PDFs and uses progress bars (`tqdm`) for user-friendly feedback.

Now, let's discuss **all the options (parameters)** in detail, including their types, defaults, interactions, and best practices.

#### 1. `input_pdf` (Required, Type: str)
   - **Description**: The full path to the input PDF file you want to process. This can be any valid PDF, including scanned documents or those with embedded text (though OCR is always used for consistency).
   - **Usage Notes**: Ensure the file exists and is readable. Relative or absolute paths are fine. If the path is invalid, a `FileNotFoundError` is raised.
   - **Example**: `"documents/confidential_report.pdf"`
   - **Interactions**: None specific, but higher-complexity PDFs (e.g., with images or tables) may benefit from increased `dpi` for better OCR results.
   - **Best Practice**: Use absolute paths to avoid working directory issues in scripts.

#### 2. `output_pdf` (Required, Type: str)
   - **Description**: The full path where the processed PDF will be saved. This will be a new file containing the annotated or redacted pages.
   - **Usage Notes**: The output is always a PDF generated from modified images, preserving the original layout as closely as possible. If the path's directory doesn't exist, it will be created implicitly by the file write operation.
   - **Example**: `"output/annotated_report.pdf"`
   - **Interactions**: Overwrites existing files without warning, so choose a unique name.
   - **Best Practice**: Include descriptive suffixes like "_redacted" or "_highlighted" to distinguish outputs.

#### 3. `target_words` (Required, Type: list)
   - **Description**: A list of strings representing the words or phrases to detect as "targets." Detection is case-insensitive and matches if any target substring appears in a word (e.g., "conf" would match "confidential").
   - **Usage Notes**: Must be a list; single strings will raise a `ValueError`. Empty list is allowed but results in no targets (useful for modes like `show_all_boxes=True`).
   - **Example**: `["confidential", "secret", "john doe"]`
   - **Interactions**: Targets are derived from or used alongside `redaction_json_path`. In redaction modes, only these words trigger changes. Combine with `only_target_boxes` to ignore non-targets.
   - **Best Practice**: Use lowercase for consistency, as matching is lowercased. For phrases, include spaces (e.g., "top secret").

#### 4. `redaction_json_path` (Required, Type: str)
   - **Description**: Path to a JSON file containing a dictionary that maps target words (keys) to their replacement strings (values). This is used during redaction to overlay custom text.
   - **Usage Notes**: The JSON must be a valid dict; invalid formats raise a `ValueError`. Keys should match `target_words` (case-insensitive). Even if not redacting, this param is required but ignored in annotation modes.
   - **Example**: `"config/redaction.json"` with content: `{"confidential": "[REDACTED]", "john doe": "[ANONYMIZED]"}`
   - **Interactions**: Essential for `redact_targets=True` (unless `black_redaction=True`, where replacements are skipped). If a target lacks a mapping, it's redacted without replacement (fallback behavior).
   - **Best Practice**: Keep keys in sync with `target_words`. Use placeholders like "[REDACTED]" for compliance.

#### 5. `show_all_boxes` (Optional, Default: False, Type: bool)
   - **Description**: If True, draws black outline boxes around **all** detected words (targets and non-targets) for comprehensive annotation. Useful for debugging OCR accuracy or visualizing text extraction.
   - **Usage Notes**: Only active when `redact_targets=False` (annotation mode). Overrides color distinctions—everything gets black boxes.
   - **Example**: Set to `True` for a full word-level markup.
   - **Interactions**: Conflicts with redaction; if `redact_targets=True`, this is ignored. Combine with `only_target_boxes=False` for maximum coverage.
   - **Best Practice**: Use for initial tests to verify word detection before applying targeted changes.

#### 6. `only_target_boxes` (Optional, Default: False, Type: bool)
   - **Description**: If True, processes (draws or redacts) only boxes containing target words, ignoring non-targets. This focuses operations on sensitive areas.
   - **Usage Notes**: Applies in both annotation and redaction modes. Reduces processing overhead on large documents.
   - **Example**: Set to `True` when you only care about highlighting/redacting specific terms.
   - **Interactions**: In annotation mode without `show_all_boxes`, targets get blue boxes, non-targets are skipped. In redaction, only targets are modified.
   - **Best Practice**: Enable for efficiency in targeted workflows; disable for broader analysis.

#### 7. `redact_targets` (Optional, Default: False, Type: bool)
   - **Description**: If True, switches to redaction mode: targets are covered (whited out or blacked out) and optionally replaced with text from the redaction dict. If False, defaults to annotation mode (drawing boxes).
   - **Usage Notes**: Primary mode toggle. In redaction, boxes are filled; no outlines are drawn.
   - **Example**: Set to `True` for privacy-focused tasks like anonymization.
   - **Interactions**: Enables `black_redaction`. If True, `show_all_boxes` is ignored. Uses `redaction_json_path` for replacements.
   - **Best Practice**: Combine with `black_redaction=False` for readable redactions (e.g., legal docs) or True for irreversible hiding.

#### 8. `black_redaction` (Optional, Default: False, Type: bool
   - **Description**: If True **and** `redact_targets=True`, fills target boxes with solid black without any replacement text. This is for permanent, non-reversible redaction.
   - **Usage Notes**: Ignores the redaction dict's replacements. Only affects targets.
   - **Example**: Set to `True` for high-security scenarios where even placeholders are too revealing.
   - **Interactions**: Requires `redact_targets=True`; otherwise ignored. No font sizing or text overlay occurs.
   - **Best Practice**: Use sparingly, as it can disrupt document flow; test with lower DPI first.

#### 9. `tesseract_cmd` (Optional, Default: None, Type: str)
   - **Description**: Optional path to the Tesseract OCR executable. If None, assumes Tesseract is in your system's PATH.
   - **Usage Notes**: Useful for custom installations or environments without PATH setup. Validates the path exists.
   - **Example**: `"C:\\Program Files\Tesseract-OCR\\tesseract.exe"` on Windows.
   - **Interactions**: Affects OCR performance. If invalid, raises `FileNotFoundError`.
   - **Best Practice**: Provide if Tesseract isn't globally available; otherwise, leave as None for simplicity.

#### 10. `dpi` (Optional, Default: 500, Type: int)
   - **Description**: The resolution (dots per inch) for rendering PDF pages as images before OCR. Higher values improve accuracy but increase processing time and memory use.
   - **Usage Notes**: Minimum practical is ~200; 500 is a good balance for most documents. Affects image size and OCR quality.
   - **Example**: `300` for faster runs, `600` for high-precision needs.
   - **Interactions**: Directly impacts OCR reliability—low DPI may miss small text. Scales with page complexity.
   - **Best Practice**: Start at 500; adjust based on document font size and trial runs.

#### 11. `verbosity` (Optional, Default: 1, Type: int)
   - **Description**: Controls output logging level: 0 (silent, no prints), 1 (basic progress bars and timings), 2 (detailed logs like word counts, phrases).
   - **Usage Notes**: Uses `print` for output and `tqdm` for progress (disabled at 0). Helps with monitoring long processes.
   - **Example**: `2` for debugging, `0` for background scripts.
   - **Interactions**: Affects all steps—e.g., at 2, you'll see per-page details.
   - **Best Practice**: Use 1 for most cases; 2 when troubleshooting OCR or grouping issues.

#### Key Interactions and Modes Summary
- **Annotation Mode** (`redact_targets=False`): Draws boxes. Use `show_all_boxes` for all words, `only_target_boxes` to focus.
- **Redaction Mode** (`redact_targets=True`): Modifies targets. Toggle `black_redaction` for style.
- **Common Pitfalls**: Ensure `target_words` matches redaction keys. Test with small PDFs first.
- **Performance**: Processing time scales with page count, DPI, and document size. For large files, lower DPI or use verbosity=1.

## Usage Examples
SpectrePDF offers versatile modes. Here are some scenarios with code snippets:

### 1. Detect and Highlight Target Words (Draw Blue Boxes)
Review a PDF by outlining targets in blue.

```python
process_pdf(
    input_pdf="report.pdf",
    output_pdf="highlighted.pdf",
    target_words=["sensitive", "private"],
    redaction_json_path="redaction.json",  # Still needed, even if not redacting
    show_all_boxes=False,  # Only draw around targets
    redact_targets=False,  # Don't redact, just annotate
    dpi=300,
    verbosity=2
)
```

**What Happens**: Pages are rendered, OCR detects words, blue boxes are drawn around matches like "sensitive", and the PDF is rebuilt.

### 2. Redact with Custom Text Replacements
Anonymize names or terms while keeping the document readable.

```python
process_pdf(
    input_pdf="patient_records.pdf",
    output_pdf="anonymized.pdf",
    target_words=["patient name", "ssn"],
    redaction_json_path="redaction.json",  # e.g., {"patient name": "[PATIENT]", "ssn": "[REDACTED]"}
    redact_targets=True,
    black_redaction=False,
    only_target_boxes=True,  # Focus only on targets
    dpi=500,
    verbosity=1
)
```

**What Happens**: Targets are whited out, replaced with fitting text (auto-sized font), and non-targets remain untouched.

### 3. Blackout Redaction for Maximum Security
Irreversibly hide sensitive info with black boxes.

```python
process_pdf(
    input_pdf="classified_doc.pdf",
    output_pdf="blacked_out.pdf",
    target_words=["top secret"],
    redaction_json_path="redaction.json",  # Replacement dict ignored in black mode
    redact_targets=True,
    black_redaction=True,
    dpi=400,
    verbosity=1
)
```

**What Happens**: Matching words/phrases are filled with solid black—no text overlay.

### 4. Debug Mode: Draw Boxes Around All Words
Inspect OCR accuracy by outlining every detected word (black for all).

```python
process_pdf(
    input_pdf="test.pdf",
    output_pdf="debug_all_boxes.pdf",
    target_words=[],  # No targets needed for this mode
    redaction_json_path="redaction.json",
    show_all_boxes=True,
    redact_targets=False,
    verbosity=2
)
```

**What Happens**: Every word gets a black outline, helping you verify layout and detection.

### Advanced Tips
- **Multi-Page PDFs**: Handles large documents efficiently with progress tracking.
- **Font Handling**: Automatically scales replacement text to fit boxes; falls back to default font if "arial.ttf" is unavailable.
- **Error Handling**: Raises informative exceptions for missing files, invalid inputs, or OCR failures.
- **Performance**: Higher DPI improves accuracy but increases processing time. Start with 300-500 DPI.

## Contributing
We welcome contributions! Fork the repo, create a branch, and submit a pull request. Ideas for improvements:
- Support for more OCR languages.
- Batch processing multiple PDFs.
- GUI integration.

Report issues on GitHub.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments
- Powered by PyMuPDF, Tesseract, and Pillow.
- Inspired by real-world needs for secure document handling.

Get started with SpectrePDF today and take control of your PDF privacy! If you have questions, check the code or open an issue. 🚀
