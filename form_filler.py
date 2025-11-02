# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.common.exceptions import TimeoutException

# # Constants for question types (assuming these are provided by your question extractor)
# QUESTION_TYPE = {
#     "SHORT_ANSWER": 0,
#     "PARAGRAPH": 1,
#     "MULTIPLE_CHOICE": 2,
#     "CHECKBOX": 3,
#     "DROPDOWN": 4,
# }

# def fill_google_form(form_url: str, questions_with_answers: list):
#     """
#     Fills a Google Form automatically using Selenium with robust waits.

#     Args:
#         form_url (str): The URL of the Google Form.
#         questions_with_answers (list): List of dictionaries containing "question", "type", and "answer".
#     """
#     options = webdriver.ChromeOptions()
#     # Keeps the browser open after the script finishes for manual review
#     options.add_experimental_option("detach", True)
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     try:
#         driver.get(form_url)
#         wait = WebDriverWait(driver, 15)  # Delay is added so that the page loads properly
        
#         # Wait for the form container to be present
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
#         print("Successfully loaded the form. Starting to fill answers...")

#         for item in questions_with_answers:
#             question_text = item["question"]
#             question_type = item.get("type") # Use .get() for safety
#             answer = item.get("answer")

#             if not answer:
#                 print(f"⏩ Skipping question '{question_text}' as no answer was provided.")
#                 continue
            
#             print(f"Answering '{question_text}' with '{answer}'")

#             try:
#                 # Find the parent div for the entire question block
#                 # This XPath looks for a div that contains the question text and has a specific role.
#                 question_block_xpath = f"//div[contains(., '{question_text}') and @role='listitem']"
#                 question_block = wait.until(EC.presence_of_element_located((By.XPATH, question_block_xpath)))

#                 # --- Handle different question types with robust waits ---

#                 # Short Answer & Paragraph
#                 if question_type in [QUESTION_TYPE["SHORT_ANSWER"], QUESTION_TYPE["PARAGRAPH"]]:
#                     # Wait for the input/textarea to be clickable within the question block
#                     input_field = wait.until(EC.element_to_be_clickable(
#                         (By.XPATH, f"{question_block_xpath}//input[@type='text'] | {question_block_xpath}//textarea")
#                     ))
#                     input_field.clear()
#                     input_field.send_keys(answer)

#                 # Multiple Choice (Radio Buttons)
#                 elif question_type == QUESTION_TYPE["MULTIPLE_CHOICE"]:
#                     # Wait for the radio button with the specific answer value to be clickable
#                     option_to_click = wait.until(EC.element_to_be_clickable(
#                         (By.XPATH, f"{question_block_xpath}//div[@data-value='{answer}']")
#                     ))
#                     option_to_click.click()

#                 # Checkboxes
#                 elif question_type == QUESTION_TYPE["CHECKBOX"]:
#                     answers_list = [answer] if not isinstance(answer, list) else answer
#                     for ans in answers_list:
#                         checkbox = wait.until(EC.element_to_be_clickable(
#                             (By.XPATH, f"{question_block_xpath}//div[@data-answer-value='{ans}']")
#                         ))
#                         checkbox.click()
                
#                 # Dropdown
#                 elif question_type == QUESTION_TYPE["DROPDOWN"]:
#                     # 1. Click the dropdown to open it
#                     dropdown_opener = wait.until(EC.element_to_be_clickable(
#                         (By.XPATH, f"{question_block_xpath}//div[@role='listbox']")
#                     ))
#                     dropdown_opener.click()
                    
#                     # 2. Wait for the specific option to appear and be clickable
#                     # The options often appear at the end of the DOM, not inside the question block.
#                     option_in_list = wait.until(EC.element_to_be_clickable(
#                         (By.XPATH, f"//div[@role='option' and @data-value='{answer}']")
#                     ))
#                     option_in_list.click()
#                     # Add a brief sleep to allow the dropdown animation to close
#                     time.sleep(0.5)

#             except TimeoutException:
#                 print(f"⚠️ Could not find or interact with question: '{question_text}'. Timed out waiting for element.")
#             except Exception as e:
#                 print(f"⚠️ An unexpected error occurred for question '{question_text}'. Error: {e}")
            
#             time.sleep(0.5) # A small delay to mimic human behavior

#         print("\n✅ Form filling complete! Please review and submit manually.")

#     except Exception as e:
#         print(f"❌ An error occurred during the form filling process: {e}")



# Filename: form_filler.py

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

# --- Private Helper Functions for Handling Question Types ---

def _handle_short_answer(wait: WebDriverWait, block_xpath: str, answer: str):
    """Waits for and fills a short answer or paragraph field."""
    locator = (By.XPATH, f"{block_xpath}//input[@type='text'] | {block_xpath}//textarea")
    input_field = wait.until(EC.element_to_be_clickable(locator))
    input_field.clear()
    input_field.send_keys(answer)

def _handle_multiple_choice(wait: WebDriverWait, block_xpath: str, answer: str):
    """Waits for and selects a multiple-choice (radio button) option."""
    locator = (By.XPATH, f"{block_xpath}//div[@data-value='{answer}']")
    option = wait.until(EC.element_to_be_clickable(locator))
    option.click()

def _handle_checkbox(wait: WebDriverWait, block_xpath: str, answer: list or str):
    """Waits for and selects one or more checkbox options."""
    answers_list = [answer] if not isinstance(answer, list) else answer
    for ans in answers_list:
        locator = (By.XPATH, f"{block_xpath}//div[@data-answer-value='{ans}']")
        checkbox = wait.until(EC.element_to_be_clickable(locator))
        checkbox.click()

def _handle_dropdown(wait: WebDriverWait, block_xpath: str, answer: str):
    """Opens a dropdown and selects the specified option."""
    # 1. Click the dropdown to open its options.
    opener_locator = (By.XPATH, f"{block_xpath}//div[@role='listbox']")
    dropdown_opener = wait.until(EC.element_to_be_clickable(opener_locator))
    dropdown_opener.click()
    
    # 2. Select the option. Google Form dropdowns often render options at the end
    #    of the document, outside the main question block.
    option_locator = (By.XPATH, f"//div[@role='option' and @data-value='{answer}']")
    option_in_list = wait.until(EC.element_to_be_clickable(option_locator))
    option_in_list.click()
    time.sleep(0.5) # Allow animation to complete.

# --- Main Function ---

def fill_google_form(form_url: str, questions_with_answers: list):
    """
    Fills a Google Form automatically using Selenium with a robust, modular approach.

    Args:
        form_url (str): The URL of the Google Form.
        questions_with_answers (list): A list of dictionaries, each containing
                                       a "question", "type", and "answer".
    """
    # Maps question type constants to their handler functions.
    QUESTION_TYPE = { "SHORT_ANSWER": 0, "PARAGRAPH": 1, "MULTIPLE_CHOICE": 2, "CHECKBOX": 3, "DROPDOWN": 4 }
    handler_map = {
        QUESTION_TYPE["SHORT_ANSWER"]: _handle_short_answer,
        QUESTION_TYPE["PARAGRAPH"]: _handle_short_answer, # Handled by the same function
        QUESTION_TYPE["MULTIPLE_CHOICE"]: _handle_multiple_choice,
        QUESTION_TYPE["CHECKBOX"]: _handle_checkbox,
        QUESTION_TYPE["DROPDOWN"]: _handle_dropdown,
    }

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(form_url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
        print("✅ Form loaded successfully. Starting automation...")

        for item in questions_with_answers:
            question_text = item["question"]
            question_type = item.get("type")
            answer = item.get("answer")

            if not answer:
                print(f"⏩ Skipping '{question_text}' (no answer provided).")
                continue
            
            print(f"Attempting to answer '{question_text}'...")

            try:
                question_block_xpath = f"//div[contains(., '{question_text}') and @role='listitem']"
                handler = handler_map.get(question_type)

                if handler:
                    handler(wait, question_block_xpath, answer)
                else:
                    print(f"⚠️ Warning: No handler defined for question type '{question_type}'.")

            except TimeoutException:
                print(f"❌ ERROR: Could not find '{question_text}'. Timed out.")
            except Exception as e:
                print(f"❌ ERROR answering '{question_text}': {e}")
        
        print("\n✅ Form filling routine complete. Please review and submit manually.")

    except Exception as e:
        print(f"❌ A critical error occurred: {e}")





# -------------------------------
# Example usage
# -------------------------------


# from answer_retrever import rag_pipeline_with_refresh 


# if __name__ == "__main__":

#     FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScP8ZvKzWqo496iHhBYp99ygcSEGADD4LOJAaXjspkYvfRBnw/viewform?usp=header"
#     # DOCUMENTS = [r"test_files\Avula_Puneeth_Kumar_Reddy_resume.pdf"]  
#     DOCUMENTS = [r"test_files\GFF_sample_context_text_file_2.pdf", r"test_files\GFF_sample_context_text_file.docx"]  # Add your files

#     print("🚀 Starting the Google Form Auto-filler Process...")
#     print(f"📄 Using document(s): {', '.join(DOCUMENTS)}")

#     print("\n🧠 Generating answers from documents... Please wait.")
#     filled_form_data = rag_pipeline_with_refresh(
#         FORM_URL, 
#         DOCUMENTS,
#         top_k=3,
#         context_refresh_interval=5
#     )
    
#     # ---  Verify the Generated Answers  ---

#     print("\n✅ Answers generated successfully. Here's what will be filled in:")
#     print("-" * 70)
#     for q in filled_form_data:
#         print(f"❓ Question: {q['question']}")
#         print(f"✔️ Answer:   {q.get('answer', 'No answer found')}") # Use .get() for safety
#         print("-" * 70)

#     # ---  Automatically Fill the Google Form ---

#     print("\n🤖 Now launching browser to auto-fill the form...")
#     fill_google_form(FORM_URL, filled_form_data)

#     print("\n🎉 Process complete! The browser window has been left open for your review.")