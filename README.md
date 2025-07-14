# SpectrePDF: Python PDF Redaction and Annotation Tool

## Overview
This project provides a Python-based tool for processing PDF documents to detect, annotate, and redact specific text using Optical Character Recognition (OCR) and image processing techniques. It leverages libraries like **PyMuPDF**, **Pillow (PIL)**, **pytesseract**, and **img2pdf** to identify target words, group them into lines, merge adjacent target word boxes, and optionally redact and replace text in the PDF. The tool is designed to be flexible, allowing users to customize the redaction process, visualize detected text with bounding boxes, and save the output as a new PDF.

## Features
- **Text Detection**: Uses Tesseract OCR to identify text and their bounding boxes in PDF pages rendered as images.
- **Target Word Identification**: Detects specified target words (case-insensitive) in the PDF content.
- **Line Grouping**: Groups words into lines based on their vertical proximity, using a threshold derived from the median word height.
- **Merged Bounding Boxes**: Combines adjacent target words into a single bounding box for consistent redaction or annotation.
- **Redaction and Replacement**: Optionally redacts target words by covering them with a white rectangle and replacing them with user-specified text from a redaction dictionary.
- **Bounding Box Visualization**: Draws colored bounding boxes around detected text (blue for target words, red for non-target words, or black for all boxes when specified).
- **Font Size Estimation**: Dynamically estimates the appropriate font size to fit replacement text within the redacted area.
- **Output Generation**: Converts processed images back into a PDF file.
- **Customizable Parameters**: Allows users to toggle redaction, choose whether to show all or only target boxes, and customize target words and replacement text.

## Dependencies
- **PyMuPDF** (`pymupdf`): For PDF handling and rendering pages as images.
- **Pillow** (`PIL`): For image processing and drawing.
- **pytesseract**: For OCR to extract text and bounding box data.
- **img2pdf**: For converting processed images back to PDF.
- **statistics**: For calculating median word height to group words into lines.

Install dependencies using:
```bash
pip install pymupdf Pillow pytesseract img2pdf
```

Additionally, you need to have **Tesseract-OCR** installed on your system and specify its path in the script (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe` for Windows).

## Usage
1. **Prepare Input PDF**: Ensure you have an input PDF file (e.g., `input.pdf`) to process.
2. **Configure Parameters**:
   - `target_words`: List of words to detect (case-insensitive).
   - `redaction_dict`: Dictionary mapping target words to their replacement text.
   - `show_all_boxes`: Set to `True` to draw black boxes around all detected words, or `False` to use blue (target) and red (non-target) boxes.
   - `only_target_boxes`: Set to `True` to draw boxes only around target words.
   - `redact_targets`: Set to `True` to redact target words and replace them with text from `redaction_dict`.
3. **Run the Script**:
   ```python
   python script.py
   ```
   The script processes the input PDF, applies the specified operations, and saves the output to `output_pdf` (e.g., `redacted.pdf`).
4. **Output**: The processed PDF will contain annotated or redacted text as per the configuration.

### Example
```python
target_words = ["first_name", "last_name", "name1", "name2", "(alphanumeric)", "name3", "name4", "group", "name"]
redaction_dict = {
    "first_name": "Homer",
    "last_name": "Simpson",
    "(alphanumeric)": "(ABC123456)",
    "name1": "The King",
    "name2": "of England",
    "name3": "Yobbo",
    "name4": "Muppet",
    "group": "123",
    "name": "456",
}
process_pdf(
    input_pdf='input.pdf',
    output_pdf='redacted.pdf',
    target_words=target_words,
    redaction_dict=redaction_dict,
    show_all_boxes=False,
    only_target_boxes=False,
    redact_targets=True
)
```

This configuration redacts target words in `input.pdf` and replaces them with corresponding values from `redaction_dict`, saving the result to `redacted.pdf`.

## Key Functions
- `estimate_font_size_for_phrase(phrase, box_width, box_height, font_path, max_iterations)`: Estimates the optimal font size to fit a replacement phrase within a bounding box, falling back to a default font if the specified font is unavailable.
- `process_pdf(input_pdf, output_pdf, target_words, redaction_dict, show_all_boxes, only_target_boxes, redact_targets)`: Main function to process the PDF, perform OCR, group words, merge boxes, and apply redaction or annotation.

## Performance
- The script measures and prints the processing time for the entire operation.
- High DPI (500) is used for rendering PDF pages to ensure accurate OCR results, which may increase processing time for large documents.

## Limitations
- Requires Tesseract-OCR to be installed and properly configured.
- Font size estimation may not always perfectly fit complex phrases due to variations in font metrics.
- The tool assumes the input PDF contains text that can be accurately detected by OCR.
- Only supports TrueType fonts or the default PIL font for text replacement.

## Future Improvements
- Add support for custom font paths and multiple font options.
- Optimize OCR performance for large PDFs by processing pages in parallel.
- Enhance line grouping logic to handle varied text layouts (e.g., multi-column documents).
- Add support for regex-based target word matching.
- Provide a GUI for easier configuration and preview of results.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

