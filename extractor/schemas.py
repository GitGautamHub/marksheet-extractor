from pydantic import BaseModel, Field
from typing import List, Optional, Any


# schemas for fields with confidence scores
class FieldWithConfidence(BaseModel):
    value: Optional[Any] = None
    confidence: float = 0.0

# schema for candidate details
class CandidateDetails(BaseModel):
    name: FieldWithConfidence
    father_name: FieldWithConfidence
    roll_no: FieldWithConfidence
    registration_no: FieldWithConfidence
    date_of_birth: FieldWithConfidence
    institution: FieldWithConfidence

# schema for examination details
class ExaminationDetails(BaseModel):
    exam_year: FieldWithConfidence
    board_university: FieldWithConfidence


# schema for subject marks
class SubjectMarks(BaseModel):
    subject: FieldWithConfidence
    max_marks: Optional[FieldWithConfidence] = None
    obtained_marks: Optional[FieldWithConfidence] = None
    credits: Optional[FieldWithConfidence] = None
    grade_obtained: Optional[FieldWithConfidence] = None
    grade_point: Optional[FieldWithConfidence] = None


# schema for overall result
class OverallResult(BaseModel):
    result: FieldWithConfidence
    grade_division: FieldWithConfidence


# schema for marksheet response
class MarksheetResponse(BaseModel):
    candidate_details: CandidateDetails
    examination_details: ExaminationDetails
    subject_wise_marks: List[SubjectMarks]
    overall_result: OverallResult
    issue_date: FieldWithConfidence