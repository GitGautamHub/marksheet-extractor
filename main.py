from fastapi import FastAPI, File, Security, UploadFile, HTTPException
from fastapi.security import APIKeyHeader
from extractor.ocr import extract_text_from_doc
from extractor.llm import get_structured_data
from extractor.scoring import calculate_confidence_score
import asyncio
from typing import List
import os
from dotenv import load_dotenv
from extractor import schemas

load_dotenv()

# FastAPI application instance
app = FastAPI(title="Marksheet Extractor",
              description="An API to extract structured data from academic marksheets.",
              version="1.0.0")

api_key_header = APIKeyHeader(name="X-API-Key")
API_KEY = os.getenv("API_KEY")


# API Key Validation
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


# File Processing
async def process_single_file(file: UploadFile):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        return {"filename": file.filename, "error": "Invalid file type."}

    file_bytes = await file.read()

    # OCR extraction
    ocr_text = extract_text_from_doc(doc_bytes=file_bytes, content_type=file.content_type)
    if not ocr_text:
        return {"filename": file.filename, "error": "Text extraction failed."}

    # LLM extraction
    llm_output = get_structured_data(ocr_text)
    if not llm_output:
        return {"filename": file.filename, "error": "Failed to get structured data from LLM."}

    response_data = {}

    # ---------------- Candidate Details ----------------
    candidate_details = llm_output.get("candidate_details", {})
    response_data["candidate_details"] = {
        k: {
            "value": v,
            "confidence": calculate_confidence_score(k, v)
        } for k, v in candidate_details.items()
    }

    # ---------------- Examination Details ----------------
    exam = llm_output.get("examination_details", {})
    response_data["examination_details"] = {
        k: {
            "value": v,
            "confidence": calculate_confidence_score(k, v)
        } for k, v in exam.items()
    }

    # ---------------- Subject Wise Marks ----------------
    marks_list = []
    for subject in llm_output.get("subject_wise_marks", []):
        subject_entry = {}
        for k, v in subject.items():
            subject_entry[k] = {
                "value": v,
                "confidence": calculate_confidence_score(k, v, context=subject)
            }
        marks_list.append(subject_entry)
    response_data["subject_wise_marks"] = marks_list

    # ---------------- Overall Result ----------------
    overall_result = llm_output.get("overall_result", {})
    response_data["overall_result"] = {
        k: {
            "value": v,
            "confidence": calculate_confidence_score(k, v)
        } for k, v in overall_result.items()
    }

    # ---------------- Issue Date ----------------
    issue_date = llm_output.get("issue_date")
    response_data["issue_date"] = {
        "value": issue_date,
        "confidence": calculate_confidence_score("issue_date", issue_date)
    }

    return {"filename": file.filename, "data": response_data}

# API Endpoint to handle batch file uploads and return extracted data
@app.post("/extract/")
async def extract_data(files: List[UploadFile] = File(...), api_key: str = Security(get_api_key)):
    tasks = [process_single_file(file) for file in files]
    results = await asyncio.gather(*tasks)
    
    return results


