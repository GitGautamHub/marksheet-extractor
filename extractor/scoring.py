import re
from dateutil.parser import parse


# to check if a date is valid
def is_valid_date(date_string: str) -> bool:
    if not date_string or not isinstance(date_string, str): return False
    try:
        parse(date_string, fuzzy=False)
        return True
    except (ValueError, TypeError):
        return False

# to check if a name contains only letters and spaces
def contains_only_letters_and_space(name: str) -> bool:
    if not name or not isinstance(name, str): return False
    return bool(re.match(r'^[A-Z\s\.]+$', name.upper()))


# to check if a value is numeric
def is_numeric(value: any) -> bool:
    if value is None: return False
    return isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit())

# to calculate confidence score based on field name and value
def calculate_confidence_score(field_name: str, value: any, context: dict = None) -> float:
    base_score = 0.85
    if value is None or str(value).strip() == "":
        return 0.0

    if field_name in ["name", "father_name", "institution", "subject"]:
        if contains_only_letters_and_space(str(value)):
            base_score += 0.10
        if any(char.isdigit() for char in str(value)):
            base_score -= 0.40

    elif field_name in ["date_of_birth", "issue_date"]:
        if is_valid_date(str(value)):
            base_score += 0.15
        else:
            base_score -= 0.40

    elif field_name == "obtained_marks":
        if not is_numeric(value):
            base_score -= 0.50
        elif context:
            max_marks = context.get('max_marks')
            if is_numeric(max_marks):
                if float(value) > float(max_marks) or float(value) < 0:
                    base_score -= 0.70

    elif field_name == "max_marks":
        if not is_numeric(value) or float(value) <= 0:
            base_score -= 0.50

    elif field_name == "exam_year":
        if not is_numeric(value):
            base_score -= 0.50
        else:
            year = int(value)
            if 1900 <= year <= 2100:
                base_score += 0.10
            else:
                base_score -= 0.50

    return max(0.0, min(1.0, round(base_score, 2)))