from playwright.sync_api import sync_playwright
import time
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os
import fitz  # PyMuPDF

# Load environment variables
load_dotenv(".env")

API_KEY = os.getenv("API_KEY")

# Set environment variables detect the file fype is pdf or docx



PDF_PATH = os.getenv("PDF_PATH")

# Initialize ZhipuAI client
client = ZhipuAI(api_key=API_KEY)

# Function to extract text from a PDF file or docxfile
def get_text_from_doc(file_path):
    """Extract text from a doc file."""
    with open(file_path, 'rb') as file:
        text = file.read()
    return text.decode('utf-8')


def get_text_from_pdf(file_path=PDF_PATH):
    """Extract text from a PDF file."""
    with fitz.open(file_path) as document:
        return "".join(page.get_text() for page in document)

def query_zhipuai(system_content, user_content, max_tokens=4095, temperature=0.5, top_p=0.5):
    """Send a query to ZhipuAI with given system and user content."""
    response = client.chat.completions.create(
        model="glm-4-0520",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stream=False
    )
    return response.choices[0].message.content

def clean_text(raw_text):
    """Clean and extract relevant job information from raw text."""
    system_content = (
        "你是一个专业的信息提取机器人，请根据用户输入的原始的未清洗的信息，"
        "提取出只包含工作岗位职责和任职要求的信息。"
    )
    return query_zhipuai(system_content, raw_text, max_tokens=8090, temperature=0.3, top_p=0.2)

def get_job_relevance(description, resume):
    """Calculate job relevance based on job description and resume."""
    system_content = (
        f"你是一个专业的相关性计算机器人，请根据用户输入的岗位信息，"
        f"计算给出的简历信息的人岗匹配相关性,要求只输出0到1的小数,要求输出必须只能是数字。\n{resume}。"
    )
    return float(query_zhipuai(system_content, description))

def get_self_introduction(job_description, resume):
    """Generate a self-introduction based on resume and job description."""
    system_content = (
        f"你是一个专业求职者，请根据给出的简历信息和岗位信息,写出一段简短的自我介绍，"
        f"字数在150字左右。要求尽可能的展示自己与岗位相关的能力，如：专业技能、项目经验、工作经历等，"
        f"要求只能从简历中的信息进行展示。\n{resume}。"
    )
    return query_zhipuai(system_content, job_description)

def process_jobs(page):
    """Process each job card and interact based on relevance."""
    resume_text = get_text_from_pdf()
    job_cards = page.query_selector_all('li.job-card-box')

    for idx, job_card in enumerate(job_cards):
        job_card.click()
        time.sleep(2)

        page.wait_for_selector('p.desc')
        job_name = page.inner_text('span.job-name')
        job_description = page.inner_text('p.desc')

        cleaned_text = clean_text(job_description)
        relevance = get_job_relevance(cleaned_text, resume_text)

        print(f'{idx}. job {job_name} relevance: {relevance}')

        if relevance >= 0.75:
            hello = get_self_introduction(cleaned_text, resume_text)
            page.click('a[href="#chat"]')  # Adjust selector as necessary
            page.wait_for_selector('#chat-input')
            page.type('#chat-input', hello)
            page.keyboard.press('Enter')
            print(f'CV sent to job {job_name}')
            page.go_back()
            page.wait_for_load_state("networkidle")
            job_cards = page.query_selector_all('li.job-card-box')
        else:
            print('Job is not relevant, skipping.')

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.zhipin.com/')
        time.sleep(5)
        page.click('a[href="https://www.zhipin.com/web/user/"]')
        page.wait_for_load_state("networkidle")
        page.click('a[href="#login"]')
        time.sleep(5)
        print('Login success')
        page.goto('https://www.zhipin.com/web/geek/job-recommend?city=101200100')
        page.wait_for_selector('div.job-list-container')
        process_jobs(page)
        browser.close()

if __name__ == "__main__":
    main()