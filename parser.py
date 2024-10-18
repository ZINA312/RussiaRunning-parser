from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import requests
from urllib.parse import urlparse


def get_events(url):
    events = []
    page = 0
    global image_id
    while True:
        driver.get(url + str(page)) 
        time.sleep(1)

        event_cards = driver.find_elements(By.CLASS_NAME, 'event-card')  

        if not event_cards:
            driver.get(url + str(page)) 
            time.sleep(10)
            event_cards = driver.find_elements(By.CLASS_NAME, 'event-card') 
            if not event_cards:
                break 

        for card in event_cards:
            try:
                cover_img = card.find_element(By.CLASS_NAME, 'event-card__cover-img')
                style = cover_img.get_attribute('style')
                image_url = style.split('url("')[1].split('")')[0]
                image_name = os.path.join('images', str(image_id), '.jpg')
                response = requests.get(image_url)
                image_url = style.split('url("')[1].split('")')[0]
                url_path = urlparse(image_url).path
                extension = os.path.splitext(url_path)[1] 
                image_name = str(image_id) + extension  # Замените на нужное имя
                response = requests.get(image_url)
                if response.status_code == 200:
                        with open('images/' + image_name, 'wb') as file:
                            file.write(response.content)
            except:
                image_name = 'default.jpg'
            urlLink = card.find_element(By.CLASS_NAME, "event-card__name").get_attribute('href')
            driver.execute_script("window.open('');")  
            driver.switch_to.window(driver.window_handles[1]) 
            driver.get(urlLink)  
            time.sleep(4)
            try:
                title = driver.find_element(By.CLASS_NAME, 'event-info__title').text
            except:
                title = ''
            try:
                date = driver.find_element(By.CLASS_NAME, 'event-intro__content').find_elements(By.CLASS_NAME, 'event-info__detail')[0].text
            except:
                date = ''
            try:
                place = driver.find_element(By.CLASS_NAME, 'event-intro__content').find_elements(By.CLASS_NAME, 'event-info__detail')[1].text
            except:
                place = ''
            try: 
                link_element = driver.find_element(By.XPATH, "//a[span[text()='Вебсайт']]")
                website = link_element.get_attribute("href")
            except:
                website = ''
            try:
                description = driver.find_element(By.ID, 'eventDescription').text
            except: 
                description = ''
            try:
                first_div = driver.find_element(By.XPATH, "//span[contains(text(), 'Вид спорта')]/ancestor::h3/parent::div")
                second_div = first_div.find_element(By.XPATH, "following-sibling::div")
                sport_texts = second_div.find_elements(By.TAG_NAME, "span")
                sport_type = ', '.join(map(lambda sport: sport.text, sport_texts))
            except:
                sport_type = ''

            events.append((title, date, place, urlLink, website, description, sport_type, image_name))
            driver.close() 
            driver.switch_to.window(original_window)
            image_id += 1

        page += 1
        
    return events

# Основная функция
def main():
    global driver, original_window, image_id
    image_id = 1

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    original_window = driver.current_window_handle
    all_events = get_events('https://russiarunning.com/events?dateFrom=2024-01-01&dateTo=2028-07-31&place&p=')
    
    
    df = pd.DataFrame(all_events, columns=['Название', 'Дата', 'Место', 'Ссылка RussiaRunning', 'Ссылка мероприятия', 'Описание', 'Вид спорта', 'Картинка'])
    df.to_excel('future_events.xlsx', index=False)
    print("Данные записаны в файл future_events.xlsx")

    all_events = get_events('https://russiarunning.com/results?dateFrom=2024-01-01&dateTo=2024-11-30&place&p=')
    df = pd.DataFrame(all_events, columns=['Название', 'Дата', 'Место', 'Ссылка RussiaRunning', 'Ссылка мероприятия', 'Описание', 'Вид спорта', 'Картинка'])
    df.to_excel('past_events.xlsx', index=False)
    print("Данные записаны в файл past_events.xlsx")
    driver.quit() 

if __name__ == "__main__":
    main()