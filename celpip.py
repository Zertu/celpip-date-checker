import time
import smtplib
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from selenium.webdriver.support.select import Select

def drop_down_selection(driver, element_id, selection):
    select_element = driver.find_element(By.ID, element_id)
    var = Select(select_element)
    var.select_by_value(selection)
    
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
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
    
    if os.environ.get('DOCKER_ENV') == 'true':
        return webdriver.Remote(
            command_executor='http://localhost:4444',
            options=options
        )
    else:
        return webdriver.Edge(options=options)

def celpip_checker():
    url = "https://www.celpip.ca/"
    print("Starting browser...")
    try:
        browser = get_webdriver()
        browser.implicitly_wait(0.5)
        browser.get(url)
        drop_down_selection(browser, "filter-type", "CELPIP-G")
        drop_down_selection(browser, "filter-country", "Canada")
        drop_down_selection(browser, "filter-region", "Newfoundland And Labrador")
        drop_down_selection(browser, "filter-city", "St. John's")
        element = browser.find_element(By.XPATH, "/html/body/main/section[2]/div/div/form/div/div[2]")
        element.click()
        time.sleep(6)

        # DOWNLOAD THE HTML CONTENT OF THE PAGE
        page = BeautifulSoup(browser.page_source, "html.parser")
        browser.quit()
        # FIND ALL THE "LI" LIST ITEM TAGS
        containers = page.findAll("div", {"class": "col-xs-1 col"})

        # ONLY KEEP THE FIRST TEN
        early_dates = containers[:10]

        # EXTRACT THE DATE COMPONENTS AND COMBINE THEM
        dates = []
        test_center = []
        for item in early_dates:
            # 检查可用性
            availability_div = item.find("div", {"class": "availability-green"})
            print(item.find("div", {"class": "date"}))
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
        
        # CONVERT THE TEXT INTO DATETIME OBJECTS
        only_dates = [datetime.strptime(date, '%b %d, %Y') for date in dates]

        # SET A THRESHOLD DATE
        date_threshold = datetime.strptime("Mar 20, 2025", '%b %d, %Y')

        # CREATE LISTS FOR AVAILABLE DATES AND TEST CENTERS
        available_slots = []

        # CHECK FOR DATES BEFORE THE THRESHOLD
        for date, center in zip(only_dates, test_center):
            if date < date_threshold:
                # Format date for display
                formatted_date = date.strftime('%b %d, %Y')
                available_slots.append(f"{formatted_date}: {center}")

        # SEND EMAIL IF AVAILABLE SLOTS ARE FOUND
        if available_slots:
            availability_info = "\n".join(available_slots)
            send_email(url, availability_info)
            print(f"Found {len(available_slots)} available slots. Email sent!")
        else:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"No available dates at {now}")
            
    except Exception as e:
        print(f"Error starting browser: {str(e)}")
    finally:
        if 'browser' in locals():
            browser.quit()
            print("Browser closed")       


def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(celpip_checker, 'interval', minutes=1)
    print("Scheduler started. Will check every minute.")
    scheduler.start()

if __name__ == "__main__":
    if os.environ.get('DOCKER_ENV') == 'true':
        try:
            start_scheduler()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")
    else:
        # celpip_checker()
        start_scheduler()