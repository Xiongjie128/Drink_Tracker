from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import time
import pandas as pd

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# go to site
driver.get("https://whisky.my/shop/")

# scroll
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

for _ in range(20):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# extract product data
items = driver.find_elements(By.CLASS_NAME, "product-small")
data = []

for item in items:
    try:
        name = item.find_element(By.CSS_SELECTOR, ".woocommerce-loop-product__title").text.strip()
    except:
        name = "N/A"

    try:
        spans = item.find_elements(By.CSS_SELECTOR, ".title-wrapper span")
        abv = spans[0].text.strip() if spans else "N/A"
    except:
        abv = "N/A"

    try:
        # extract image url
        image_url = item.find_element(By.CSS_SELECTOR, ".box-image img").get_attribute("src")
    except:
        image_url = "N/A"

    data.append({
        "name": name,
        "abv": abv,
        "image_url": image_url
    })

driver.quit()
# save results
df = pd.DataFrame(data).drop_duplicates()
df = df[~df.isin(["N/A"]).any(axis=1)]
df.reset_index(drop=True, inplace=True)
df.head(10)

df.to_csv("alcohol_data_with_url.csv", index=False)