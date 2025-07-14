# SpectrePDF: Python PDF Redaction and Annotation Tool

## Overview
This package provides a Python-based tool for processing PDF documents to detect, annotate, and redact specific text using Optical Character Recognition (OCR) and image processing techniques. It leverages libraries like **PyMuPDF**, **Pillow (PIL)**, **pytesseract**, and **img2pdf** to identify target words, group them into lines, merge adjacent target word boxes, and optionally redact and replace text in the PDF. The tool is designed to be flexible, allowing users to customize the redaction process, visualize detected text with bounding boxes, and save the output as a new PDF.

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
- **Modular Design**: Exposes multiple helper functions for advanced customization, such as rendering pages, performing OCR, collecting words, grouping lines, merging boxes, and more.

## Dependencies
- **PyMuPDF** (`pymupdf>=1.24.0`): For PDF handling and rendering pages as images.
- **Pillow** (`PIL>=10.0.0`): For image processing and drawing.
- **pytesseract** (`>=0.3.10`): For OCR to extract text and bounding box data.
- **img2pdf** (`>=0.5.1`): For converting processed images back to PDF.
- **statistics**: For calculating median word height to group words into lines (included in Python standard library).

Install the package and its dependencies using:
```bash
pip install SpectrePDF
```

Additionally, you need to have **Tesseract-OCR** installed on your system. Download and install from [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract). Ensure `tesseract` is in your PATH, or provide the path via the `tesseract_cmd` parameter in `process_pdf`.

## Usage
1. **Install the Package**: Use the command above to install `pdf-SpectrePDF`.
2. **Import and Configure**:
   - Import the main function: `from SpectrePDF import process_pdf`
   - Define `target_words`: List of words to detect (case-insensitive).
   - Define `redaction_dict`: Dictionary mapping target words to their replacement text.
   - Set flags: `show_all_boxes`, `only_target_boxes`, `redact_targets`.
3. **Process the PDF**:
   ```python
   from SpectrePDF import process_pdf

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
       redact_targets=True,
       tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # Optional, adjust as needed
       dpi=500
   )
   ```
   This processes `input.pdf`, applies redaction to target words, and saves the result to `redacted.pdf`.
4. **Output**: The processed PDF will contain annotated or redacted text as per the configuration.

## Key Functions
- `estimate_font_size_for_phrase(phrase, box_width, box_height, font_path="arial.ttf", max_iterations=10)`: Estimates the optimal font size to fit a replacement phrase within a bounding box, falling back to a default font if the specified font is unavailable.
- `process_pdf(input_pdf, output_pdf, target_words, redaction_dict, show_all_boxes=False, only_target_boxes=False, redact_targets=False, tesseract_cmd=None, dpi=500)`: Main function to process the PDF, perform OCR, group words, merge boxes, and apply redaction or annotation.
- `render_pages_to_images(doc, dpi=500)`: Renders PDF pages to PIL images.
- `perform_ocr(img)`: Performs OCR on an image.
- `collect_words(ocr_data, target_words)`: Collects word data from OCR results.
- `group_words_into_lines(words)`: Groups words into lines based on vertical position.
- `merge_target_groups(line)`: Merges adjacent target words in a line and collects boxes.
- `create_merged_box(group, is_target)`: Creates a merged box from a group of words.
- `create_single_box(word, is_target)`: Creates a box from a single word.
- `collect_boxes(lines, only_target_boxes=False)`: Collects boxes from lines, optionally filtering non-targets.
- `get_replacement_phrase(words, redaction_dict)`: Constructs replacement phrase for redaction.
- `redact_box(draw, box, redaction_dict)`: Redacts a box and draws replacement text.
- `draw_box_outline(draw, box, color)`: Draws outline around a box.
- `process_boxes(draw, boxes, redact_targets, redaction_dict, show_all_boxes)`: Processes boxes: redacts or draws outlines.
- `save_image_to_bytes(img)`: Saves PIL image to bytes.

For advanced usage, import these functions from `SpectrePDF`.

## Performance
- The script measures and prints the processing time for the entire operation.
- High DPI (default 500) is used for rendering PDF pages to ensure accurate OCR results, which may increase processing time for large documents.

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
