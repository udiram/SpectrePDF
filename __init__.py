
from SpectrePDF.anonymizer import estimate_font_size_for_phrase, process_pdf, render_pages_to_images, perform_ocr, collect_words, group_words_into_lines, merge_target_groups, create_merged_box, create_single_box, collect_boxes, get_replacement_phrase, redact_box, draw_box_outline, process_boxes, save_image_to_bytes

__all__ = ["estimate_font_size_for_phrase", "process_pdf", "render_pages_to_images", "perform_ocr", "collect_words", "group_words_into_lines", "merge_target_groups", "create_merged_box", "create_single_box", "collect_boxes", "get_replacement_phrase", "redact_box", "draw_box_outline", "process_boxes", "save_image_to_bytes"]

__version__ = "0.2.1"