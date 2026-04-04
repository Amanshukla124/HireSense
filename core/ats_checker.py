import re

def check_ats_compliance(resume_text: str) -> list:
    """
    Checks the resume string for common ATS filtering triggers.
    Returns a list of dictionaries with { "name": str, "passed": bool, "message": str }.
    """
    text_lower = resume_text.lower()
    results = []

    # 1. Contact Information
    has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text))
    has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text))
    
    if has_email and has_phone:
        results.append({"name": "Contact Info", "passed": True, "message": "Email and phone number found."})
    else:
        results.append({"name": "Contact Info", "passed": False, "message": "Missing email or phone number. ATS systems use these to create your profile."})

    # 2. Standard Headers
    headers = ["experience", "education", "skills"]
    found_headers = [h for h in headers if re.search(r'\b' + h + r'\b', text_lower)]
    
    if len(found_headers) == len(headers):
        results.append({"name": "Standard Sections", "passed": True, "message": "Found Experience, Education, and Skills sections."})
    elif len(found_headers) > 0:
        results.append({"name": "Standard Sections", "passed": False, "message": f"Missing some standard headers. Found: {', '.join(found_headers)}, but expected Experience, Education, and Skills."})
    else:
        results.append({"name": "Standard Sections", "passed": False, "message": "Missing standard headers like 'Experience' or 'Education'. Non-standard names (e.g. 'My Professional Journey') confuse ATS."})

    # 3. Quantifiable Metrics (Numbers, %, $)
    has_metrics = bool(re.search(r'\d+%|\$\d+|\d+x', resume_text)) or bool(re.search(r'\b(percent|dollars)\b', text_lower))
    if has_metrics:
        results.append({"name": "Quantifiable Metrics", "passed": True, "message": "Found data points (%, $, numbers) backing up achievements."})
    else:
        results.append({"name": "Quantifiable Metrics", "passed": False, "message": "Very few numbers or metrics found. Recruiters want to see measurable impact (e.g., 'Increased sales by 15%')."})

    # 4. Action Verbs
    action_verbs = ['managed', 'developed', 'created', 'designed', 'led', 'built', 'improved', 'optimized', 'reduced', 'increased', 'implemented']
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    
    if verb_count >= 3:
        results.append({"name": "Action Verbs", "passed": True, "message": "Strong use of past/present tense action verbs."})
    else:
        results.append({"name": "Action Verbs", "passed": False, "message": "'Managed', 'Developed', 'Led', etc. are missing or underutilized. Start bullet points with strong verbs."})

    return results
