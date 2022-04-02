from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need 
from email.mime.text import MIMEText
# import sys
# sys.path.insert(0, '..')
# from secret import config
import config
import pathlib
from selenium.common.exceptions import NoSuchElementException

def main():
    item_details_list = []
    search_query = 'https://nextdoor.com/for_sale_and_free/?init_source=more_menu&is_free=true'
    scriptDirectory = pathlib.Path().absolute()
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={scriptDirectory}\\userdata") 

    driver = webdriver.Chrome(executable_path=config.chrome_path, chrome_options=chrome_options)
    driver.get(search_query)

    if (check_if_need_login(driver, "signin_button")):
        username = driver.find_element_by_id("id_email")
        password = driver.find_element_by_id("id_password")
        username.send_keys(config.nd_username)
        password.send_keys(config.nd_password)

        driver.find_element_by_id("signin_button").click()
    
    time.sleep(5)

    while True == True:
        item_list = driver.find_elements_by_xpath("//a[@class='fsf-item-detail-link classified-item-card-container']")

        for each_item in item_list:
            # Getting item info
            item_price = each_item.find_elements_by_xpath(".//div[@class='classified-item-card-price']")[0]
            item_name = each_item.find_elements_by_xpath(".//span[@class='classified-item-card-title css-xy8fxv']")[0]
            item_timelocation = each_item.find_elements_by_xpath(".//div[@class='classified-item-card-subline']")[0]
            # Saving job info 
            item_info = [item_name.text, item_timelocation.text]
            # Save into job_details if new item
            item_time = item_timelocation.text.split("ago")[0]
            if "hr" in item_time:
                item_min = item_time.split()[0]
                item_min = int(item_min) * 60
            elif "day" in item_time:
                item_min = item_time.split()[0]
                item_min = int(item_min) * 60 * 24
            else:
                item_min = item_time.split()[0]

            if (int(item_min) < 15):
                item_details_list.append(item_info)

        driver.quit()

        msg_body = ''
        for item_details in item_details_list:
            msg_body += """  
              
            New Item:  
            """ + item_details[0] + """  
            Updated 
            """ + item_details[1]

        if (len(msg_body) > 0):
            msg = MIMEText(msg_body)
            sender = config.email_sender
            to = config.email_receiver
            msg['Subject'] = 'New Free Items on Nextdoor'
            msg['From'] = sender
            msg['To'] = to

            server = smtplib.SMTP(config.smtp_address)
            server.starttls()
            server.login(sender, config.email_web_app_password)
            server.sendmail(sender, [to], msg.as_string())
            server.quit()
        
        time.sleep(900)
        driver = webdriver.Chrome(executable_path=config.chrome_path, chrome_options=chrome_options)
        driver.get(search_query)
        time.sleep(5)

def check_if_need_login(driver, id):
    try:
        driver.find_element_by_id(id)
    except NoSuchElementException:
        return False
    return True

main()    