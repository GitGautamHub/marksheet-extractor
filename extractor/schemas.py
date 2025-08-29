from pydantic import BaseModel, Field
from typing import List, Optional, Any

class FieldWithConfidence(BaseModel):
    value: Optional[Any] = None
    confidence: float = 0.0

class CandidateDetails(BaseModel):
    name: FieldWithConfidence
    father_name: FieldWithConfidence
    roll_no: FieldWithConfidence
    registration_no: FieldWithConfidence
    date_of_birth: FieldWithConfidence
    institution: FieldWithConfidence

class ExaminationDetails(BaseModel):
    exam_year: FieldWithConfidence
    board_university: FieldWithConfidence

class SubjectMarks(BaseModel):
    subject: FieldWithConfidence
    max_marks: Optional[FieldWithConfidence] = None
    obtained_marks: Optional[FieldWithConfidence] = None
    credits: Optional[FieldWithConfidence] = None
    grade_obtained: Optional[FieldWithConfidence] = None
    grade_point: Optional[FieldWithConfidence] = None

class OverallResult(BaseModel):
    result: FieldWithConfidence
    grade_division: FieldWithConfidence

class MarksheetResponse(BaseModel):
    candidate_details: CandidateDetails
    examination_details: ExaminationDetails
    subject_wise_marks: List[SubjectMarks]
    overall_result: OverallResult
    issue_date: FieldWithConfidence