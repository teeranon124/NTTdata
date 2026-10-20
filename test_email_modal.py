import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1600,1050")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print("Navigating to http://127.0.0.1:8080/ ...")
    driver.get("http://127.0.0.1:8080/")
    time.sleep(2)

    # 1. Trigger openEmailModal('nsk')
    print("Opening AWS SES Email Simulation Modal...")
    driver.execute_script("app.openEmailModal('nsk');")
    time.sleep(1)

    # Check modal visibility
    modal = driver.find_element(By.ID, "email_sim_modal")
    is_open = modal.get_attribute("open")
    print(f"Modal open attribute: {is_open}")

    subject = driver.find_element(By.ID, "email-subject-line").text
    recipient = driver.find_element(By.ID, "email-recipient-address").text
    sku = driver.find_element(By.ID, "email-body-sku").text
    qty = driver.find_element(By.ID, "email-body-qty").text
    portal_href = driver.find_element(By.ID, "email-portal-link-btn").get_attribute("href")

    print(f"Subject: {subject}")
    print(f"Recipient: {recipient}")
    print(f"SKU: {sku}")
    print(f"Qty: {qty}")
    print(f"Portal Link: {portal_href}")

    # Take screenshot of open modal
    driver.save_screenshot("aws_ses_email_modal.png")
    print("Saved screenshot to aws_ses_email_modal.png")

    # 2. Test opening another deal's email modal, e.g. skf
    driver.execute_script("app.openEmailModal('skf');")
    time.sleep(1)
    sku_skf = driver.find_element(By.ID, "email-body-sku").text
    qty_skf = driver.find_element(By.ID, "email-body-qty").text
    portal_skf = driver.find_element(By.ID, "email-portal-link-btn").get_attribute("href")
    print(f"[SKF Test] SKU: {sku_skf}, Qty: {qty_skf}, Link: {portal_skf}")

    driver.save_screenshot("aws_ses_email_modal_skf.png")
    print("Saved screenshot to aws_ses_email_modal_skf.png")

finally:
    driver.quit()
    print("Test completed.")
