import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import datetime
from selenium.webdriver.support.ui import Select
import os

def send_email(url, availability_info):
    msg = EmailMessage()
    sender_email = os.environ.get('e_user')
    app_password = os.environ.get('e_pwd')
    recipient_email = os.environ.get('e_client')
    
    msg["Subject"] = "Test Centre is available!"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.set_content(
        f"Hi,\n\nThere may be some seats available in:\n\n{availability_info}\n\nCheck out the link:\n{url}")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
            print("Email sent!")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def celpip_checker():
    url = "https://secure.celpip.ca/RegWebApp/#/registration/test-selection"
    print("Starting browser...")
    browser = None

    try:
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')  # 只显示 FATAL 级别的日志
        options.add_argument('--silent')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        
        browser = webdriver.Edge(options=options)
        print("Browser started successfully")
        browser.get(url)
        print(f"Accessing URL: {url}")
        browser.implicitly_wait(20)
        
        # 获取页面内容
        page_source = browser.page_source
        page = BeautifulSoup(page_source, 'html.parser')
        print("Page content retrieved")
        
        # 找到所有日期容器
        containers = page.findAll("div", {"class": "col-xs-1 col"})
        print(f"Found {len(containers)} date containers")

        # 只保留前10个
        early_dates = containers[:10]
        dates = []
        test_center = []
        
        for item in early_dates:
            # 检查可用性
            availability_div = item.find("div", {"class": "availability-green"})
            
            if availability_div:  # 如果找到 availability-green class，说明有位置
                date_div = item.find("div", {"class": "date"})
                if date_div:
                    month = date_div.find_all("span")[1].text
                    day = date_div.find_all("span")[2].text
                    year = str(datetime.now().year)
                    date_str = f"{month} {day}, {year}"
                    dates.append(date_str)
                    
                    # 同时添加对应的考试中心
                    center = item.find_next("div", {"class": "address"}).text.strip()
                    test_center.append(center)

        # 转换为datetime对象进行比较
        only_dates = [datetime.strptime(date, '%b %d, %Y') for date in dates]
        
        # 设置阈值日期
        date_threshold = datetime.strptime("Mar 20, 2025", '%b %d, %Y')
        
        available_slots = []
        
        # 检查日期并添加可用时段
        for date, center in zip(only_dates, test_center):
            if date < date_threshold:
                formatted_date = date.strftime('%b %d, %Y')
                available_slots.append(f"{formatted_date}: {center}")
        
        # 如果有可用时段，发送邮件
        if available_slots:
            availability_info = "\n".join(available_slots)
            send_email(url, availability_info)
            print(f"Found {len(available_slots)} available slots. Email sent!")
        else:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"No available dates at {now}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
    finally:
        if browser is not None:
            browser.quit()
            print("Browser closed")

if __name__ == "__main__":
    try:
        celpip_checker()
    except Exception as e:
        print(f"Script failed: {str(e)}")