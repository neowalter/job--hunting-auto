from playwright.sync_api import sync_playwright
import time 
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os 
import fitz  # PyMuPDF

def read_env(file_path):
    load_dotenv(file_path)

read_env(".env")

API_KEY = os.getenv("API_KEY")
PDF_PATH = os.getenv("PDF_PATH")


def get_text_from_pdf():
    # 打开PDF文件
    file_path = PDF_PATH
    document = fitz.open(file_path)
    text = ""
    # 遍历每一页
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    document.close()
    return text


def clean_text(text):
    # remove the irrelevant characters and informations
    raw_text = text
    api_key = API_KEY
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
    model="glm-4-0520",
        messages=[
            {
                "role": "system",
                "content": """你是一个专业的信息提取机器人，请根据用户输入的原始的未清洗的信息，提取出只包含工作岗位职责和任职要求的信息。
                例如用户输入：“岗位职责：
1、负责日常运营，整体规划 营销 推广 及产品优化；
2、提升店铺及产品流量关键词营销,从而能够有效提升店铺及产品的访问量；
3、熟悉平台推广流程及活动策划和提报；
4、协助主管建设管理好团队及完成上级交代的其它工作内容；
5、制定月度销售任务和服务水平提升目标，制定月度店铺推广预算；负责策划店铺促销活动方案，执行与配合官方相关营销活动，带领管理团队完成预期销售目标。
任职要求：
1、大专及以上学历，从事淘宝/天猫运营二年以上经验；
2、熟悉淘宝/天猫/京东交易规则、营销推广体系和运营环境；
3、擅长营销,对产品促销活动有较强的策划和执行能力；
4、有较强的数据分析能力,能够根据深入细致的数据分析进行产品和活动的优化；
5、具有良好的沟通和协作精神，工作细致耐心，具有强烈的责任心和事业心；
福利待遇:
1、每年不定期旅游，团建聚餐；
2、上班时间8:45-18:00，大小周，法定节假日正常休息；
3、购买社保；
4、享有带薪年假。”
你的输出应该为：“岗位职责：
1、负责日常运营，整体规划 营销 推广 及产品优化；
2、提升店铺及产品流量关键词营销,从而能够有效提升店铺及产品的访问量；
3、熟悉平台推广流程及活动策划和提报；
4、协助主管建设管理好团队及完成上级交代的其它工作内容；
5、制定月度销售任务和服务水平提升目标，制定月度店铺推广预算；负责策划店铺促销活动方案，执行与配合官方相关营销活动，带领管理团队完成预期销售目标。
任职要求：
1、大专及以上学历，从事淘宝/天猫运营二年以上经验；
2、熟悉淘宝/天猫/京东交易规则、营销推广体系和运营环境；
3、擅长营销,对产品促销活动有较强的策划和执行能力；
4、有较强的数据分析能力,能够根据深入细致的数据分析进行产品和活动的优化；
5、具有良好的沟通和协作精神，工作细致耐心，具有强烈的责任心和事业心；”
                """
            },
            {
                "role": "user",
                "content": raw_text
            }
        ],
        top_p= 0.2,
        temperature= 0.3,
        max_tokens=8090,
        stream=False,
        )

    return str(response.choices[0].message.content)

def get_job_relevance(description):
    api_key = API_KEY
    client = ZhipuAI(api_key=api_key)
    resume = get_text_from_pdf()
    response = client.chat.completions.create(
    model="glm-4-0520",
        messages=[
            {
                "role": "system",
                "content": """你是一个专业的相关性计算机器人，请根据用户输入的岗位信息，计算给出的简历信息的人岗匹配相关性,要求只输出0到1的小数,要求输出必须只能是数字。
{}。
例如用户输入：“岗位职责：
1、配合需求部门，设计和编写提示工程所需的相关指令数据， 并配合进行持续优化。
2、小型数据标注需求的支持及对代加工等相关数据进行质检 品控，确保数据质量
3. 精通Python
4. 熟悉AI大模型的原理，有本地化部署AI大模型的经历
5. 熟悉大模型的训练调优，有训练调优的经历
6. 熟悉rag，有嵌入上下文文本训练的经验
7. 熟悉其他AI模型或工具为佳（StableDiffusion、lama等
你的回复应该是：“0.6”
""".format(resume)
},
            {
                "role": "user",
                "content": description
            }
        ],
        top_p= 0.5,
        temperature= 0.5,
        max_tokens=4095,
        stream=False,
    )

    return response.choices[0].message.content


def get_hello(text):
    api_key = API_KEY
    client = ZhipuAI(api_key=api_key)
    resume = get_text_from_pdf()
    response = client.chat.completions.create(
    model="glm-4-0520",
        messages=[
            {
                "role": "system",
                "content": """你是一个专业求职者，请根据给出的简历信息和岗位信息,写出一段简短的自我介绍，字数在150字左右。要求尽可能的展示自己与岗位相关的能力，如：专业技能、项目经验、工作经历等，要求只能从简历中的信息进行展示。
{}，
例如用户输入：“岗位职责：1、通过在线平台接收客户的技术咨询和问题，提供相应的解决方案与建议，必要时进行培训教学；
2、解决并跟踪用户的技术问题，确保问题得到圆满解决。收集用户反馈与建议，与产研等团队沟通，为产品功能优化、客户体验提升等维度提供建议；
3、沉淀总结高质量的教程与帮助文档，协助用户更好地理解和应用RPA相关指令、开发RPA应用；
4、分析客户高频问题，为AI智能机器人提供有效的知识库内容，提升其问题解答能力。
岗位要求：1、全日制重点本科及以上学历，计算机相关专业，熟练掌握Python编程语言；
2、具备优秀的表达与解决问题的能力，能够清晰地传达技术知识和提供指导；
3、具备团队合作精神与积极创新意识，能够适应快节奏的工作环境，有IT技术支持相关岗位经验者优先；
4、对于开发者社区发展与知识分享有热情，助力开发者生态，贡献价值。
你的回复应该是：“您好！我是XX，一名计算机科学硕士毕业生，对贵公司的RPA技术支持工程师岗位非常感兴趣。
我在XX公司担任客户工程师期间，曾通过Python构建聊天群机器人，有效降低了客诉处理时间并提高了应答率。
此外，我还开发了一个基于微信桌面端的智能自动回复机器人，集成了网络爬虫、文本摘要和问答功能。
这些经验与贵司岗位要求高度契合，尤其是在提供技术支持、优化用户体验和开发AI辅助工具方面。
我具备良好的沟通能力和问题解决能力，能够快速适应新环境并持续学习。我相信我的技术背景和创新精神将为贵公司的RPA技术支持团队带来价值。
期待能有机会进一步讨论如何为贵公司的发展做出贡献。”
""".format(resume)
},
            {
                "role": "user",
                "content": text,
            }
        ],
        top_p= 0.3,
        temperature= 0.7,
        max_tokens=4095,
        stream=False,
    )

    return response.choices[0].message.content



with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,  # 是否无头模式
    )
    page = browser.new_page()
    # city = '101020100'
    # job = '远程客服'
    # full_url = 'https://www.zhipin.com/web/geek/job?query={job}&city={city}'.format(job=job, city=city)
    # print(full_url)
    url = 'https://www.zhipin.com/'
    page.goto(url)
    time.sleep(5)
    # page.screenshot(path='example.png')
    page.click('a[href="https://www.zhipin.com/web/user/"]')
    page.wait_for_load_state("networkidle")
    page.click('//*[@id="wrap"]/div/div[2]/div[2]/div[2]/div[1]/div[4]/a')
    time.sleep(5)
    print('login success')
    # get the text from the job description
    # Wait for the job list container to load
    page.goto('https://www.zhipin.com/web/geek/job-recommend?city=101200100')
    page.wait_for_selector('div.job-list-container')
    # Select all job card boxes
    job_cards = page.query_selector_all('li.job-card-box')
    # job_descriptions = []
    for idx in range(len(job_cards)):
        # Click on the job card
        job_cards = page.query_selector_all('li.job-card-box')
        job_cards[idx].click()

        time.sleep(2)
        # Wait for any necessary elements to load after the click
        page.wait_for_timeout(500)  # Adjust timeout as needed
        # Extract the description text
        page.wait_for_selector('p.desc')
        job_name = page.inner_text('//*[@id="wrap"]/div[2]/div[2]/div/div/div[2]/div/div[1]/div[1]/div/span[1]')
        job_description =  page.inner_text('p.desc')
        # print(job_description)
        cleaned_text = clean_text(job_description)
        # time.sleep(2)
        relevant = get_job_relevance(cleaned_text)
        print('{}. job {} relevance: {}'.format(idx, job_name,relevant))
        hello = get_hello(cleaned_text)
        if float(relevant) >= 0.75:
            # this will redirect to the chat page
            page.click('//*[@id="wrap"]/div[2]/div[2]/div/div/div[2]/div/div[1]/div[2]/a[2]')
            page.wait_for_selector('//*[@id="chat-input"]')
            time.sleep(2)
            page.type('//*[@id="chat-input"]', hello)
            time.sleep(2)
            page.keyboard.press('Enter')
            print('cv sent to job {}'.format(job_name))
            # this will go back to the job card page but can't continue the for loop how to fix this 
            page.go_back()
            page.wait_for_load_state("networkidle")
            job_cards = page.query_selector_all('li.job-card-box')
        else:
            print('job is not relevant, fire it ')

    browser.close()

