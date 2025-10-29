import re
import json
import requests

def extract_questions_from_google_form(form_url):
    # Step 1: Follow redirects if the link is shortened (forms.gle)
    try:
        session = requests.Session()
        response = session.head(form_url, allow_redirects=True)
        expanded_url = response.url
    except Exception:
        expanded_url = form_url

    # Step 2: Ensure proper URL ending
    if not expanded_url.endswith("viewform"):
        if not expanded_url.endswith("/"):
            expanded_url += "/viewform"
        else:
            expanded_url += "viewform"

    # Step 3: Fetch the form HTML
    response = requests.get(expanded_url)
    html = response.text

    # Step 4: Extract embedded JSON (FB_PUBLIC_LOAD_DATA_)
    match = re.search(r'FB_PUBLIC_LOAD_DATA_ = (.*?);</script>', html)
    if not match:
        raise ValueError("Could not extract form data. Check if the link is public and valid.")

    data_str = match.group(1)
    data = json.loads(data_str)

    # Step 5: Extract questions
    questions = []
    for item in data[1][1]:
        try:
            question_text = item[1]
            question_type = item[3]
            options = []
            if question_type in [2, 3, 4]:  # multiple choice / checkbox / dropdown
                if item[4] and isinstance(item[4], list):
                    for opt in item[4][0][1]:
                        options.append(opt[0])
            questions.append({
                "question": question_text,
                "type": question_type,
                "options": options
            })
        except Exception:
            continue

    return questions


