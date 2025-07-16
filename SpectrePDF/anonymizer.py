import pymupdf  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import img2pdf
from io import BytesIO
import time
import statistics
from tqdm import tqdm
import os
import json

def estimate_font_size_for_phrase(phrase, box_width, box_height, font_path="arial.ttf", max_iterations=10):
    """
    Estimate font size to fit the phrase within the box width and height.
    Returns a PIL ImageFont object with the appropriate size.
    """
    font_size = int(box_height * 0.8)
    if font_size < 6:
        font_size = 6
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception as e:
        print(f"Error loading font {font_path}: {e}. Using default font.")
        font = ImageFont.load_default()
        return font
    temp_img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    for _ in range(max_iterations):
        text_bbox = draw.textbbox((0, 0), phrase, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        if text_width <= box_width and text_height <= box_height:
            break
        font_size = int(font_size * 0.9)
        if font_size < 6:
            font_size = 6
            try:
                font = ImageFont.truetype(font_path, font_size)
            except Exception:
                font = ImageFont.load_default()
            break
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()
            break
    return font

def render_pages_to_images(doc, dpi=500, verbosity=1):
    """Render PDF pages to PIL images."""
    images = []
    total_pages = len(doc)
    iterable = tqdm(range(total_pages), desc="Rendering pages", disable=verbosity < 1)
    for page_num in iterable:
        if verbosity >= 2:
            print(f"Rendering page {page_num + 1}/{total_pages}")
        page = doc[page_num]
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def perform_ocr(img, verbosity=1):
    """Perform OCR on the image."""
    if verbosity >= 2:
        print("Performing OCR...")
    try:
        return pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang='eng')
    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

def collect_words(ocr_data, target_words, verbosity=1):
    """Collect word data from OCR results."""
    words = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i]
        if not text.strip():
            continue
        x = ocr_data['left'][i]
        y = ocr_data['top'][i]
        width = ocr_data['width'][i]
        height = ocr_data['height'][i]
        is_target = any(target_word.lower() in text.lower() for target_word in target_words)
        words.append({'text': text, 'x': x, 'y': y, 'width': width, 'height': height, 'is_target': is_target})
    if verbosity >= 2:
        print(f"Collected {len(words)} words from OCR data")
    return words

def group_words_into_lines(words, verbosity=1):
    """Group words into lines based on vertical position."""
    if not words:
        return []
    heights = [word['height'] for word in words]
    median_height = statistics.median(heights)
    threshold = 0.5 * median_height

    lines = []
    current_line = []
    current_y = None
    for word in words:
        if current_y is None or word['y'] - current_y > threshold:
            if current_line:
                lines.append(current_line)
            current_line = [word]
            current_y = word['y']
        else:
            current_line.append(word)
    if current_line:
        lines.append(current_line)
    if verbosity >= 2:
        print(f"Grouped words into {len(lines)} lines")
    return lines

# def merge_target_groups(line, verbosity=1):
#     """Merge adjacent target words in a line and collect boxes."""
#     boxes = []
#     current_group = []
#     for word in line:
#         if word['is_target']:
#             current_group.append(word)
#         else:
#             if current_group:
#                 boxes.append(create_merged_box(current_group, is_target=True))
#                 current_group = []
#             boxes.append(create_single_box(word, is_target=False))
#     if current_group:
#         boxes.append(create_merged_box(current_group, is_target=True))
#     if verbosity >= 2:
#         print(f"Merged {len(boxes)} boxes in line")
#     return boxes

def merge_target_groups(line, verbosity=1):
    """Never merge: each target word gets its own box."""
    boxes = []
    for word in line:
        boxes.append(create_single_box(word, is_target=word['is_target']))
    if verbosity >= 2:
        print(f"Merged {len(boxes)} boxes in line")
    return boxes

def create_merged_box(group, is_target):
    """Create a merged box from a group of words."""
    if not group:
        raise ValueError("Cannot create merged box from empty group")
    min_x = min(w['x'] for w in group)
    min_y = min(w['y'] for w in group)
    max_x = max(w['x'] + w['width'] for w in group)
    max_y = max(w['y'] + w['height'] for w in group)
    return {
        'x': min_x,
        'y': min_y,
        'width': max_x - min_x,
        'height': max_y - min_y,
        'is_target': is_target,
        'words': group.copy()
    }

def create_single_box(word, is_target):
    """Create a box from a single word."""
    return {
        'x': word['x'],
        'y': word['y'],
        'width': word['width'],
        'height': word['height'],
        'is_target': is_target,
        'words': [word]
    }

def collect_boxes(lines, only_target_boxes=False, verbosity=1):
    """Collect boxes from lines, optionally filtering non-targets."""
    boxes_to_draw = []
    for line in lines:
        line_boxes = merge_target_groups(line, verbosity=verbosity)
        for box in line_boxes:
            if only_target_boxes and not box['is_target']:
                continue
            boxes_to_draw.append(box)
    if verbosity >= 2:
        print(f"Collected {len(boxes_to_draw)} boxes in total")
    return boxes_to_draw

def get_replacement_phrase(words, redaction_dict):
    """Construct replacement phrase for redaction."""
    replacement_parts = []
    for word in words:
        text = word['text']
        replaced = False
        for target_word, replacement in redaction_dict.items():
            if target_word.lower() in text.lower():
                replacement_parts.append(replacement)
                replaced = True
                break
        if not replaced:
            replacement_parts.append(text)
    return ' '.join(replacement_parts)

def redact_box(draw, box, redaction_dict, black_redaction=False, verbosity=1):
    """Redact a box: fill with black if black_redaction, else white and draw replacement text."""
    try:
        if black_redaction:
            draw.rectangle([(box['x'], box['y']), (box['x'] + box['width'], box['y'] + box['height'])], fill='black')
        else:
            draw.rectangle([(box['x'], box['y']), (box['x'] + box['width'], box['y'] + box['height'])], fill='white')
            replacement_phrase = get_replacement_phrase(box['words'], redaction_dict)
            if verbosity >= 2:
                print(f"Redacting with phrase: '{replacement_phrase}'")
            font = estimate_font_size_for_phrase(replacement_phrase, box['width'], box['height'])
            text_bbox = draw.textbbox((0, 0), replacement_phrase, font=font)
            text_height = text_bbox[3] - text_bbox[1]
            x = box['x']
            y = box['y'] + (box['height'] - text_height) / 2
            draw.text((x, y), replacement_phrase, fill='black', font=font)
    except Exception as e:
        raise RuntimeError(f"Redaction failed for box: {e}")

def draw_box_outline(draw, box, color):
    """Draw outline around a box."""
    draw.rectangle(
        [(box['x'], box['y']), (box['x'] + box['width'], box['y'] + box['height'])],
        outline=color
    )

def process_boxes(draw, boxes, redact_targets, redaction_dict, show_all_boxes, black_redaction=False, verbosity=1):
    """Process boxes: redact or draw outlines."""
    for box in boxes:
        if redact_targets and box['is_target']:
            redact_box(draw, box, redaction_dict, black_redaction, verbosity=verbosity)
        elif not redact_targets:
            if show_all_boxes:
                color = 'black'
            else:
                color = 'blue' if box['is_target'] else 'red'
            draw_box_outline(draw, box, color)

def save_image_to_bytes(img):
    """Save PIL image to bytes."""
    try:
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        raise RuntimeError(f"Failed to save image to bytes: {e}")

def process_pdf(input_pdf, output_pdf, target_words, redaction_json_path, show_all_boxes=False, only_target_boxes=False, redact_targets=False, black_redaction=False, tesseract_cmd=None, dpi=500, verbosity=1):
    """
    Process a PDF to detect, optionally draw boxes around, or redact and replace specific target words using OCR.

    :param input_pdf: Path to the input PDF file.
    :param output_pdf: Path to the output PDF file.
    :param target_words: List of words to target for detection or redaction.
    :param redaction_json_path: Path to the JSON file containing the redaction dictionary (mapping targets to replacements).
    :param show_all_boxes: If True, draw black boxes around all detected words.
    :param only_target_boxes: If True, only process target words/boxes.
    :param redact_targets: If True, redact and replace target words instead of drawing boxes.
    :param black_redaction: If True (and redact_targets=True), fill target boxes with black without replacement text.
    :param tesseract_cmd: Optional path to the Tesseract executable. If None, assumes it's in PATH.
    :param dpi: DPI for rendering pages (higher for better OCR accuracy).
    :param verbosity: Verbosity level (0: silent, 1: basic progress, 2: detailed logs).
    """
    start_time = time.time()

    if verbosity >= 1:
        print(f"Starting PDF processing: {input_pdf} -> {output_pdf}")
        print(f"Target words: {target_words}")
        print(f"Redaction JSON path: {redaction_json_path}")
        print(f"Options: show_all_boxes={show_all_boxes}, only_target_boxes={only_target_boxes}, redact_targets={redact_targets}, black_redaction={black_redaction}, dpi={dpi}")

    if not isinstance(target_words, list):
        raise ValueError("target_words must be a list")
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    if not os.path.exists(redaction_json_path):
        raise FileNotFoundError(f"Redaction JSON not found: {redaction_json_path}")

    try:
        with open(redaction_json_path, 'r') as f:
            redaction_dict = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load redaction JSON: {e}")

    if not isinstance(redaction_dict, dict):
        raise ValueError("Loaded redaction data must be a dict")

    if verbosity >= 1:
        print(f"Loaded redaction dict: {redaction_dict}")

    if tesseract_cmd:
        if not os.path.exists(tesseract_cmd):
            raise FileNotFoundError(f"Tesseract executable not found: {tesseract_cmd}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        doc = pymupdf.open(input_pdf)
    except Exception as e:
        raise RuntimeError(f"Failed to open PDF: {e}")

    try:
        images = render_pages_to_images(doc, dpi=dpi, verbosity=verbosity)

        modified_images = []
        iterable = tqdm(images, desc="Processing pages", disable=verbosity < 1)
        for img in iterable:
            if verbosity >= 2:
                print("Starting page processing...")
            ocr_data = perform_ocr(img, verbosity=verbosity)
            words = collect_words(ocr_data, target_words, verbosity=verbosity)
            lines = group_words_into_lines(words, verbosity=verbosity)
            boxes = collect_boxes(lines, only_target_boxes=only_target_boxes, verbosity=verbosity)
            draw = ImageDraw.Draw(img)
            process_boxes(draw, boxes, redact_targets, redaction_dict, show_all_boxes, black_redaction, verbosity=verbosity)
            modified_images.append(save_image_to_bytes(img))
            if verbosity >= 2:
                print("Page processing completed")

        with open(output_pdf, 'wb') as f:
            f.write(img2pdf.convert(modified_images))

        if verbosity >= 1:
            print(f"Output PDF saved: {output_pdf}")

    except Exception as e:
        raise RuntimeError(f"Processing failed: {e}")
    finally:
        doc.close()

    end_time = time.time()
    if verbosity >= 1:
        print(f"Processing completed successfully.")
        print(f"Total processing time: {end_time - start_time:.2f} seconds")
