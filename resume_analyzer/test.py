import random
import fitz  # PyMuPDF
import cv2
import numpy as np
import base64
import json
from collections import Counter
from PIL import Image
import io
from typing import Dict, List, Tuple
import google.generativeai as genai


data={
  "specific_issues": [
          {
            "description": "Inconsistent font usage across the document. There are 5 different fonts used throughout, which detracts from professionalism and cohesiveness.",
            "page": 1,
            "bbox": [
              0,
              0,
              612,
              792
            ]
          },
          {
            "description": "The 'Career Objective' and 'Work Experiences' headers use a grey background, which looks outdated. This could be made simpler using bold fonts, larger fonts, or lines to separate the headers from the content.",
            "page": 0,
            "bbox": [
              50,
              285,
              560,
              310
            ]
          },
          {
            "description": "The name at the top is large, but the section titles ('Career Objective', 'Work Experiences') are not emphasized enough and are only slightly different from the body text.",
            "page": 2,
            "bbox": [
              50,
              285,
              560,
              310
            ]
          }
        ]
}



import fitz  # PyMuPDF

import fitz  # PyMuPDF

def annotate_pdf_with_comments(pdf_path, output_path, issues):
    doc = fitz.open(pdf_path)

    for issue in issues:
        page_number = issue.get("page")
        bbox = issue.get("bbox")
        description = issue.get("description", "No description")

        if page_number is None or bbox is None:
            continue

        try:
            page = doc[page_number]
            rect = fitz.Rect(bbox)

            # Draw yellow filled rectangle (background)
            page.draw_rect(rect, color=(1, 0, 0), width=2.5)  # red border, yellow fill

            # Text settings
            fontsize = 10
            fontname = "helv"
            line_height = fontsize + 2
            approx_char_width = fontsize * 0.6
            max_chars_per_line = int(rect.width / approx_char_width)

            # Word wrapping
            words = description.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = (current_line + " " + word).strip()
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            total_text_height = line_height * len(lines)
            text = "🔍 " + "\n".join(lines)

            if total_text_height <= rect.height:
                target_rect = rect
            else:
                target_rect = fitz.Rect(
                    rect.x0,
                    rect.y1 + 5,
                    rect.x1,
                    rect.y1 + 5 + total_text_height
                )

                # Draw yellow background for below text
                page.draw_rect(target_rect, color=(1, 0, 0), width=2.5)

            # Insert red text on yellow background
            page.insert_textbox(
                target_rect,
                text,
                fontsize=fontsize,
                fontname=fontname,
                color=(1, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT,
                # overlay=True
            )

        except Exception as e:
            print(f"Error annotating page {page_number}: {e}")

    doc.save(output_path)
    doc.close()
    return output_path






annotate_pdf_with_comments(
        "Pawan Sapkota CV-Python.pdf",
        f"result_resume/{random.randint(1,100000)}_annotated_resume.pdf",
        data['specific_issues']
    )