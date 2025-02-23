import time
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import datetime
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

def get_webdriver():
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    # 根据环境使用不同的配置
    if os.environ.get('DOCKER_ENV') == 'true':
        # Docker 环境使用远程连接
        return webdriver.Remote(
            command_executor='http://localhost:4444',
            options=options
        )
    else:
        # 本地环境直接使用 Edge
        return webdriver.Edge(options=options)

def celpip_checker():
    url = "https://secure.celpip.ca/RegWebApp/#/registration/test-selection"
    print("Starting browser...")
    browser = None

    try:
        browser = get_webdriver()
        print("Browser started successfully")
        browser.get(url)
        print(f"Accessing URL: {url}")
        browser.implicitly_wait(20)
        
        # ... rest of your code ...
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
    finally:
        if browser is not None:
            browser.quit()
            print("Browser closed")

if __name__ == "__main__":
    # 在 Docker 中循环运行
    if os.environ.get('DOCKER_ENV') == 'true':
        while True:
            try:
                celpip_checker()
            except Exception as e:
                print(f"Script failed: {str(e)}")
            time.sleep(600)  # 每10分钟运行一次
    else:
        # 本地环境只运行一次
        celpip_checker()