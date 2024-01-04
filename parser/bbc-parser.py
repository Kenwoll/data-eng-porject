import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = 'https://www.bbc.com/news'
header_class = "lx-stream-post__header-title gel-great-primer-bold qa-post-title gs-u-mt0 gs-u-mb-"
summary_class = "lx-stream-related-story--summary qa-story-summary"

categories = ['world', 'business']
data_list = []

for category in categories:
    print(f"Target category is {category}")

    driver.get(f'{url}/{category}')
    time.sleep(5)

    for i in range(1, 50):
        print(f"scrapping page {i}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        content = soup.find('ol', class_='gs-u-m0 gs-u-p0 lx-stream__feed qa-stream')

        for item in content.find_all('li'):
            heading = item.find('h3', class_=header_class)
            link = item.find('a', href=True)
            summary = item.find('p', class_=summary_class)

            text = ''

            if link is not None:
                response = requests.get(urljoin(url, link.get('href')))
                inner_soup = BeautifulSoup(response.content, 'html.parser')
                paragraphs = inner_soup.find_all('p', class_='ssrcss-1q0x1qg-Paragraph e1jhz7w10')
                for par in paragraphs[:-1]:
                    if par is not None:
                        text += par.get_text()

            if heading is not None and link is not None and summary is not None:
                data_list.append({
                    'category': category,
                    'Heading': heading.get_text(),
                    'Summary': summary.get_text(),
                    'Link': urljoin(url, link.get('href')),
                    'Text': text
                })
        
        print(f'clicking button {i+1}')
        button = driver.find_element(By.XPATH, f'//a[contains(@href, "/page/{i+1}")]')
        button.click()

driver.quit()
df = pd.DataFrame(data_list)
df.to_csv('output_data.csv', index=False)