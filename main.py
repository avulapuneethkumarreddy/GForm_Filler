
from question_retrever import extract_questions_from_google_form

if __name__ == "__main__":
    # form_link = 'https://forms.gle/96DAsYWgk9L46BQR9'  # shortened link
    form_link = 'https://docs.google.com/forms/d/e/1FAIpQLSfvmog8uvV40h_nKduwyhMZIDpgeN7jast_svApxudt9SUjHA/viewform?usp=dialog'  # shortened link
    questions = extract_questions_from_google_form(form_link)

    print("\nExtracted Questions:\n")
    for q in questions:
        print(f"Question: {q['question']}")
        print(f"Type: {q['type']}")
        if q['options']:
            print(f"Options: {q['options']}")
        print("-" * 50)
