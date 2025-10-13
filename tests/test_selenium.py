from selenium import webdriver
from selenium.webdriver.common.by import By

def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # run headless (no GUI)
    options.add_argument("--no-sandbox")    # required in some Linux environments
    options.add_argument("--disable-dev-shm-usage")  # prevent resource issues

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    title = driver.title
    print(f"Page title: {title}")

    driver.implicitly_wait(0.5)

    text_box = driver.find_element(By.NAME, "my-text")
    submit_button = driver.find_element(By.CSS_SELECTOR, "button")

    text_box.send_keys("Selenium")
    submit_button.click()

    message = driver.find_element(By.ID, "message")
    print(f"Message: {message.text}")

    driver.quit()

if __name__ == "__main__":
    main()
