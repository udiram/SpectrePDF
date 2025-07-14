import pymupdf  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import img2pdf
from io import BytesIO
import time
import statistics

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
    except:
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
            font = ImageFont.truetype(font_path, font_size)
            break
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
            break
    return font

def process_pdf(input_pdf, output_pdf, target_words, redaction_dict, show_all_boxes=False, only_target_boxes=False, redact_targets=False):
    start_time = time.time()

    # Open the PDF using PyMuPDF
    doc = pymupdf.open(input_pdf)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as needed

    # Render each page as a PIL image
    images = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=500)  # High DPI for better OCR accuracy
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    # Process each image
    modified_images = []
    for img in images:
        # Perform OCR
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, lang='eng')
        draw = ImageDraw.Draw(img)

        # Step 1: Collect word data
        words = []
        for i in range(len(ocr_data['text'])):
            text = ocr_data['text'][i]
            if not text.strip():  # Skip empty text
                continue
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            width = ocr_data['width'][i]
            height = ocr_data['height'][i]
            is_target = any(target_word.lower() in text.lower() for target_word in target_words)
            words.append({'text': text, 'x': x, 'y': y, 'width': width, 'height': height, 'is_target': is_target})

        # Step 2: Group words into lines
        heights = [word['height'] for word in words]
        median_height = statistics.median(heights) if heights else 0
        threshold = 0.5 * median_height  # Threshold for new line detection

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

        # Step 3: Merge adjacent target boxes and collect boxes to draw
        boxes_to_draw = []
        for line in lines:
            current_group = []
            for word in line:
                if word['is_target']:
                    current_group.append(word)
                else:
                    if current_group:
                        min_x = min(w['x'] for w in current_group)
                        min_y = min(w['y'] for w in current_group)
                        max_x = max(w['x'] + w['width'] for w in current_group)
                        max_y = max(w['y'] + w['height'] for w in current_group)
                        boxes_to_draw.append({
                            'x': min_x,
                            'y': min_y,
                            'width': max_x - min_x,
                            'height': max_y - min_y,
                            'is_target': True,
                            'words': current_group.copy()
                        })
                        current_group = []
                    if not only_target_boxes:
                        boxes_to_draw.append({
                            'x': word['x'],
                            'y': word['y'],
                            'width': word['width'],
                            'height': word['height'],
                            'is_target': False,
                            'words': [word]
                        })
            if current_group:
                min_x = min(w['x'] for w in current_group)
                min_y = min(w['y'] for w in current_group)
                max_x = max(w['x'] + w['width'] for w in current_group)
                max_y = max(w['y'] + w['height'] for w in current_group)
                boxes_to_draw.append({
                    'x': min_x,
                    'y': min_y,
                    'width': max_x - min_x,
                    'height': max_y - min_y,
                    'is_target': True,
                    'words': current_group.copy()
                })

        # Step 4: Process boxes (redact and replace or draw)
        for box in boxes_to_draw:
            if redact_targets and box['is_target']:
                # Redact the entire merged box
                draw.rectangle([(box['x'], box['y']), (box['x'] + box['width'], box['y'] + box['height'])], fill='white')
                # Construct replacement phrase
                replacement_parts = []
                for word in box['words']:
                    text = word['text']
                    for target_word, replacement in redaction_dict.items():
                        if target_word.lower() in text.lower():
                            replacement_parts.append(replacement)
                            break
                    else:
                        replacement_parts.append(text)
                replacement_phrase = ' '.join(replacement_parts)
                # Estimate font size to fit the phrase
                font = estimate_font_size_for_phrase(replacement_phrase, box['width'], box['height'])
                # Calculate text position (left-aligned, vertically centered)
                text_bbox = draw.textbbox((0, 0), replacement_phrase, font=font)
                text_height = text_bbox[3] - text_bbox[1]
                x = box['x']
                y = box['y'] + (box['height'] - text_height) / 2
                # Draw the replacement text
                draw.text((x, y), replacement_phrase, fill='black', font=font)
            elif not redact_targets:
                # Draw the box
                if show_all_boxes:
                    color = 'black'
                else:
                    color = 'blue' if box['is_target'] else 'red'
                draw.rectangle(
                    [(box['x'], box['y']), (box['x'] + box['width'], box['y'] + box['height'])],
                    outline=color
                )

        # Save modified image
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        modified_images.append(img_byte_arr.getvalue())

    # Step 5: Convert to PDF
    with open(output_pdf, 'wb') as f:
        f.write(img2pdf.convert(modified_images))

    end_time = time.time()
    print(f"Processing time: {end_time - start_time} seconds")

if __name__ == "__main__":
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
        redact_targets=True  # Enable redaction and text replacement for merged boxes
    )