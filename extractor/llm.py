import os
import json
import logging
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """
You are an expert AI assistant specialized in extracting structured information from OCR text of academic mark sheets.
Your task is to parse the raw text and return a clean, structured JSON object.

Crucially, the content of the `subject_wise_marks` and `overall_result` objects should adapt to the type of marksheet.
- For Marks-Based Sheets: Populate `max_marks`, `obtained_marks`, `theory_marks`, `practical_marks`, and `total_marks` if available.
- For Grade-Based Sheets: Populate `credits`, `grade_obtained`, and `grade_point`. The marks-related fields might be null.

Do not include any explanations, introductory text, or markdown formatting. Only output the raw JSON object.

The required flexible JSON schema is:
{{
  "candidate_details": {{
    "name": "string",
    "father_name": "string",
    "mother_name": "string | null",
    "roll_no": "string",
    "registration_no": "string | null",
    "date_of_birth": "string (YYYY-MM-DD)",
    "institution": "string"
  }},
  "examination_details": {{
    "exam_year": "integer",
    "board_university": "string"
  }},
  "subject_wise_marks": [
    {{
      "subject": "string",
      "max_marks": "integer | 100",
      "obtained_marks": "integer | null",
      "theory_marks": "integer | null",
      "practical_marks": "integer | null",
      "total_marks": "integer | null",
      "credits": "integer | null",
      "grade_obtained": "string | null",
      "grade_point": "number | null"
    }}
  ],
  "overall_result": {{
    "result": "string (e.g., 'PASS', 'FAIL')",
    "grade_division": "string | null",
    "sgpa": "number | null",
    "cgpa": "number | null",
    "grand_total": "integer | null"
  }},
  "issue_date": "string (YYYY-MM-DD) | null"
}}

If a value is not found for any field, use null.

Here is the raw OCR text:
---
{ocr_text}
---
"""

def get_structured_data(ocr_text: str) -> dict:
    """
    Calls the Gemini API to convert raw OCR text to structured JSON.
    """
    if not ocr_text:
        logging.warning("OCR text is empty, skipping LLM call.")
        return {}
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = PROMPT_TEMPLATE.format(ocr_text=ocr_text)
        
        logging.info("Calling Gemini API...")
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        return json.loads(response_text)

    except Exception as e:
        logging.error(f"Error calling LLM or parsing JSON: {e}")
        return {}