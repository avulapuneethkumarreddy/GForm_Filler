import os
import platform
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# def get_driver():
#     options = Options()
#     options.add_argument("--headless=new")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     if os.getenv("RENDER"):
#         print("🧠 Running on Render — installing Chromium...")
#         subprocess.run(["apt-get", "update"], check=False)
#         subprocess.run(["apt-get", "install", "-y", "chromium", "chromium-driver"], check=False)
#         chrome_path = "/usr/bin/chromium"
#         driver_path = "/usr/bin/chromedriver"
#         options.binary_location = chrome_path
#         return webdriver.Chrome(service=Service(driver_path), options=options)
#     else:
#         print("💻 Running locally — using webdriver-manager")
#         from webdriver_manager.chrome import ChromeDriverManager
#         return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


# driver = get_driver()

# --- Private Helper Functions remain the same ---
def _handle_short_answer(wait: WebDriverWait, block_xpath: str, answer: str):
    locator = (By.XPATH, f"{block_xpath}//input[@type='text'] | {block_xpath}//textarea")
    input_field = wait.until(EC.element_to_be_clickable(locator))
    input_field.clear()
    input_field.send_keys(answer)

def _handle_multiple_choice(wait: WebDriverWait, block_xpath: str, answer: str):
    locator = (By.XPATH, f"{block_xpath}//div[@data-value='{answer}']")
    option = wait.until(EC.element_to_be_clickable(locator))
    option.click()

def _handle_checkbox(wait: WebDriverWait, block_xpath: str, answer: list or str):
    answers_list = [answer] if not isinstance(answer, list) else answer
    for ans in answers_list:
        locator = (By.XPATH, f"{block_xpath}//div[@data-answer-value='{ans}']")
        checkbox = wait.until(EC.element_to_be_clickable(locator))
        checkbox.click()

def _handle_dropdown(wait: WebDriverWait, block_xpath: str, answer: str):
    opener_locator = (By.XPATH, f"{block_xpath}//div[@role='listbox']")
    dropdown_opener = wait.until(EC.element_to_be_clickable(opener_locator))
    dropdown_opener.click()
    option_locator = (By.XPATH, f"//div[@role='option' and @data-value='{answer}']")
    option_in_list = wait.until(EC.element_to_be_clickable(option_locator))
    option_in_list.click()
    time.sleep(0.5)

def get_chrome_driver():
    """Auto-detect OS and return a configured Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    system_name = platform.system().lower()

    if system_name == "windows":
        # 🖥️ Local Windows: use visible Chrome with webdriver_manager
        options.add_experimental_option("detach", True)
        print("🖥️ Detected Windows — using local ChromeDriver.")
        service = Service(ChromeDriverManager().install())

    else:
        # ☁️ Render / Linux: use headless Chrome
        print("☁️ Detected Linux/Render — using headless Chrome.")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")

        # Typical Chrome binary paths for Render / Linux
        # chrome_bin = "/usr/bin/google-chrome"
        # chromedriver_path = "/usr/bin/chromedriver"

        # Use paths from Render's buildpack env vars, with fallbacks
        chrome_bin = os.environ.get("CHROMIUM_PATH", "/usr/bin/google-chrome")
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        if os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
        else:
            print("⚠️ Chrome binary not found at /usr/bin/google-chrome")

        if not os.path.exists(chromedriver_path):
            print("⚠️ ChromeDriver not found at /usr/bin/chromedriver, using webdriver_manager fallback")
            service = Service(ChromeDriverManager().install())
        else:
            service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def fill_google_form(form_url: str, questions_with_answers: list):
    """Main form-filling function."""
    QUESTION_TYPE = {
        "SHORT_ANSWER": 0, "PARAGRAPH": 1,
        "MULTIPLE_CHOICE": 2, "CHECKBOX": 3, "DROPDOWN": 4
    }

    handler_map = {
        QUESTION_TYPE["SHORT_ANSWER"]: _handle_short_answer,
        QUESTION_TYPE["PARAGRAPH"]: _handle_short_answer,
        QUESTION_TYPE["MULTIPLE_CHOICE"]: _handle_multiple_choice,
        QUESTION_TYPE["CHECKBOX"]: _handle_checkbox,
        QUESTION_TYPE["DROPDOWN"]: _handle_dropdown,
    }

    print("🤖 Now launching browser to auto-fill the form...")
    driver = get_chrome_driver()

    try:
        driver.get(form_url)
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
        print("✅ Form loaded successfully. Starting automation...")

        for item in questions_with_answers:
            question_text = item["question"]
            question_type = item.get("type")
            answer = item.get("answer")

            if "DATA_NOT_FOUND" in str(answer):
                print(f"⏩ Skipping '{question_text}' (answer is DATA_NOT_FOUND).")
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


# # -------------------------------
# # Example usage
# # -------------------------------


from answer_retrever import rag_pipeline_with_refresh 


if __name__ == "__main__":

    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScP8ZvKzWqo496iHhBYp99ygcSEGADD4LOJAaXjspkYvfRBnw/viewform?usp=header"
    DOCUMENTS = [r"test_files\Avula_Puneeth_Kumar_Reddy_resume.pdf"]  
    # DOCUMENTS = [r"test_files\GFF_sample_context_text_file_2.pdf", r"test_files\GFF_sample_context_text_file.docx"]  # Add your files

    print("🚀 Starting the Google Form Auto-filler Process...")
    print(f"📄 Using document(s): {', '.join(DOCUMENTS)}")

    print("\n🧠 Generating answers from documents... Please wait.")
    filled_form_data = rag_pipeline_with_refresh(
        FORM_URL, 
        DOCUMENTS,
        top_k=3,
        context_refresh_interval=5
    )
    
    # ---  Verify the Generated Answers  ---

    print("\n✅ Answers generated successfully. Here's what will be filled in:")
    print("-" * 70)
    for q in filled_form_data:
        print(f"❓ Question: {q['question']}")
        print(f"✔️ Answer:   {q.get('answer', 'No answer found')}") # Use .get() for safety
        print("-" * 70)

    # ---  Automatically Fill the Google Form ---

    fill_google_form(FORM_URL, filled_form_data)

    print("\n🎉 Process complete! The browser window has been left open for your review.")