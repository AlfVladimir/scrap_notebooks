
import re
import time
import sqlite3 as sl
from datetime import datetime

import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():

    # БД sqlite
    con = sl.connect('nb.db')
    db_create_tb(con)

    # Настройки веб драйвера
    chrome_options = webdriver.ChromeOptions()

    chrome_options.page_load_strategy = 'eager'

    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('--ignore-ssl-errors')

    driver = uc.Chrome(options = chrome_options)

    # Лист с перечнем что парсим, и функции для парсинга и функция перехода на страницы
    PARSE_LIST = [
                    ['Озон',
                    'https://www.ozon.ru/category/noutbuki-15692/',
                    ozon_parse ,
                    ozon_nextpage
                    ],
                    # ['М.Видео',
                    # 'https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118?from=under_search&showCount=72',
                    # #'https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118?from=under_search',
                    # mvideo_parse ,
                    # mvideo_nextpage
                    # ],                              
    ]

    # Сколько страниц парсим на каждый источник
    PAGE_COUNT = 10

    for parsing_site in PARSE_LIST:
        
        # Счетчик страниц
        cur_page = 1 
        
        # начальный URL
        next_page = parsing_site[1]
        # функция для парсинга: разделение на карточки и разбор по нужным полям
        parsing_fun = parsing_site[2]
        # функция которая ищет ссылку на следующую страницу и осуществляет переход
        nextpage_fun = parsing_site[3]

        # Старт с первой страницы
        driver.get(next_page)
        
        print(f"Парсим {parsing_site[0]}:")

        while cur_page < PAGE_COUNT+1 and next_page:

            time.sleep(1)

            parsing_data = parsing_fun(driver)
            # if parsing_data == []:
            #     # На странице кончились данные (нет смысла продолжать)
            #     break
            
            db_insert_tb(con, parsing_data)

            print(f"Страница - {cur_page}, карточек собрали - {len(parsing_data)}")

            cur_page+=1

            if cur_page < PAGE_COUNT+1 and not nextpage_fun(driver, cur_page):
                #Если не смогли перейти на новую страницу
                break

            # if cur_page < PAGE_COUNT+1 and next_page:
            #     # Если нашли ссылку на следующую страницу то кликаем 
            #     # эмитация человека
            #     ac = ActionChains(driver)
            #     ac.move_to_element(next_page).move_by_offset(13,12).click().perform()


    #time.sleep(10)
    
    con.close()
    driver.quit()


def find_el_none(driver: webdriver, byselector : By , selector : str): 
    """
        Поиск элемента, без ошибки если не нашли (в этом случае None)
    """
    try:
        ret = driver.find_element(byselector,selector)
    except:
        return None
    return ret

def find_eles_none(driver: webdriver, byselector : By , selector : str):
    """
        Поиск элементов, без ошибки если не нашли (в этом случае [])
    """
    try:
        ret = driver.find_elements(byselector,selector)
    except:
        return []
    return ret

def mvideo_nextpage(driver: webdriver,  cur_page: int):
    """
        Поиск следующей страницы на сайте mvideo.ru
    """
    next_page_text = 'page='+str(cur_page)
    try:
        next_page = driver.find_element(By.XPATH,f"//*[contains(@href,'{ next_page_text }')]")
    except:
        return None
    driver.get(next_page.get_attribute('href'))
    return next_page



def mvideo_parse(driver: webdriver):
    """
        Парсинг mvideo.ru
        Идентификаторы статические (за пару дней не менялись)
        можно привязываться к id
    """  

    # Ждём загрузки карточки товара (хотя бы одной)
    cards = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, r"//*[contains(@class, 'product-cards-layout__item')]"))
    )

    ret_list = []
    cards = find_eles_none(driver, By.XPATH , r"//*[contains(@class, 'product-cards-layout__item')]")

    # Карточки lazy load - загружаются, в случае, если становятся видимыми
    # делаем прокрутку мышкой по каждому товару
    for card in cards:
        ActionChains(driver)\
            .scroll_to_element(card)\
            .perform()

    # Заново получаем карточки с товарами
    cards = find_eles_none(driver, By.XPATH , r"//*[contains(@class, 'product-cards-layout__item')]")

    for card in cards:
        if not find_el_none(card, By.XPATH, ".//*[@class='product-title__text']"):
            # Если карточка пустая (не успела загрузиться или блок рекламы - бывает)
            continue

        # Собственно парсинг
        c_url = card.find_element(By.XPATH,".//*[@class='product-title__text']").get_attribute('href')
        c_visited_at = str(datetime.now())
        c_name = card.find_element(By.XPATH,".//*[@class='product-title__text']").text
        c_name = re.sub(r'[а-яА-ЯёЁ]*[ а-яА-ЯёЁ]*([^а-яА-ЯёЁ]+)',r'\1', c_name).strip()

        c_cpu_hhz = card.find_element(By.XPATH,".//span[contains(text(),'Процессор')]/following-sibling::span[text()]").text
        c_cpu_hhz = re.sub(r'[\w ]+ (\d+\.?\d*) ГГц',r'\1', c_cpu_hhz)
        c_cpu_hhz = float(c_cpu_hhz) if c_cpu_hhz.replace('.','').isdigit() else 0

        c_screen_size = find_el_none(card,By.XPATH,".//span[contains(text(),'Диагональ/')]/following-sibling::span[text()]")
        c_screen_size = c_screen_size.text if c_screen_size else ''
        c_screen_size = float(re.search('\d+\.?\d*', c_screen_size)[0].replace(',','.'))

        c_ram_gb = find_el_none(card,By.XPATH,".//span[contains(text(),'RAM')]/following-sibling::span[text()]")
        c_ram_gb = int(c_ram_gb.text) if c_ram_gb else 0

        c_ssd_gb = find_el_none(card, By.XPATH, ".//span[contains(text(),'Объем SSD')]/following-sibling::span[text()]")
        c_ssd_gb_text = c_ssd_gb.text if c_ssd_gb else ''
        c_ssd_gb = int(re.search('\d+', c_ssd_gb_text )[0]) if c_ssd_gb else 0
        c_ssd_gb = c_ssd_gb * 1024 if 'ТБ' in c_ssd_gb_text else c_ssd_gb
        

        c_price_rub = card.find_element(By.XPATH,".//*[@class='price__main-value']").text

        c_price_rub = find_el_none(card,By.XPATH,".//*[@class='price__main-value']")
        c_price_rub = int(re.search('\d+ \d*', c_price_rub.text)[0].replace(' ','')) if c_price_rub else 0
 
        ret_list.append([c_url, c_visited_at, c_name, c_cpu_hhz, c_screen_size, c_ram_gb, c_ssd_gb, c_price_rub])
       
    return ret_list

def ozon_nextpage(driver: webdriver,  cur_page: int):
    """
        Поиск следующей страницы на сайте ozon.ru
    """    
    next_page_text = 'page='+str(cur_page)
    try:
        next_page = driver.find_element(By.XPATH,f"//*[contains(@href,'{ next_page_text }')]")
    except:
        return None
    driver.get(next_page.get_attribute('href'))
    return next_page

def ozon_parse(driver: webdriver):
    """
        Парсинг ozon.ru
        все идентификаторы динамические, меняются названия классов примерно раз в сутки
        ищем какой нибудь элемент (корзину), от него относительный путь
    """       
    ret_list = []

    body = driver.find_element(By.CSS_SELECTOR,'body')
    time.sleep(1)
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1)
    body.send_keys(Keys.END)
    
        

    cards = find_eles_none(driver, By.XPATH , r"//*[contains(text(),'В корзину')]/../../../../../../../..")   
 

    
    for card in cards:

        card_text = card.text.replace('\n',' ')
        
        c_url = find_el_none(card, By.XPATH, ".//*[contains(@href,'/')]")
        c_url = c_url.get_attribute('href') if c_url else ''
        c_url = c_url.split('/?')[0]

        c_visited_at = str(datetime.now())

        c_name = re.search(r'оутбук ([^а-яА-ЯеЁ\,\*]+)\,|\*', card_text)
        c_name = c_name[1] if c_name else ''

        if not c_name:
            continue
        
        c_cpu_hhz = re.sub(r"(.*)(\()(\d+(\.|\,)?\d*)( ГГц\).*)", "\\3", card_text, 0, re.DOTALL)
        c_cpu_hhz = float(c_cpu_hhz) if c_cpu_hhz.replace('.','').isdigit() else 0

        #c_screen_size = re.sub(r"([^\"\d]*)(\d+)(\.|\,)?(\d*)(\".*)", "\\2.\\4", card_text, 0, re.DOTALL)
        #c_screen_size = float(c_screen_size)

        c_screen_size = re.search(r'\s(\d+(\.|\,)?\d*)\"', card_text)
        c_screen_size = float(c_screen_size[1].replace(',','.')) if c_screen_size else 0

        c_ram_gb = re.search('Оперативная память: (\d+) ГБ', card_text)
        c_ram_gb = int(c_ram_gb[1]) if c_ram_gb else 0


        c_ssd_gb = re.search('SSD, ГБ:\s(\d+)\s', card_text)
        c_ssd_gb = int(c_ssd_gb[1]) if c_ssd_gb else 0

        #//*[contains(text(),'₽')]
        c_price_rub = find_el_none(card, By.XPATH, ".//*[contains(text(),'₽')]")
        c_price_rub = c_price_rub.text if c_price_rub else ''
        c_price_rub = c_price_rub.replace(' ','').replace('\u2009','').replace('₽','')
        c_price_rub = int(c_price_rub)
        # c_price_rub = re.search('\d+ \d*', c_price_rub)[0]
        # c_price_rub = int(c_price_rub.replace(' ',''))


        ret_list.append([c_url, c_visited_at, c_name, c_cpu_hhz, c_screen_size, c_ram_gb, c_ssd_gb, c_price_rub])
        #print([c_url, c_visited_at, c_name, c_cpu_hhz, c_screen_size, c_ram_gb, c_ssd_gb, c_price_rub])
    #return []
    return ret_list

def db_insert_tb(con, data):
    """
        Вставка в БД спарсеных данных
    """
    sql = """
        INSERT INTO computers
        (url, visited_at, name, cpu_hhz, screen_in, ram_gb, ssd_gb, price_rub)
        values
        (?,?,?,?,?,?,?,?)
        """
    with con:
        con.executemany(sql, data)

    con.commit()



def db_create_tb(con : sl.Connection):
    """
        Создание таблицы и очистка (если существует)
    """
    with con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS computers(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
            url varchar,
            visited_at timestamp,
            name varchar,
            cpu_hhz float,
            screen_in float,
            ram_gb int,
            ssd_gb int,
            price_rub int,
            rank float generated always as 
            ( 
                0
                + 10 * cpu_hhz
                + 4 * screen_in
                + 15 * ram_gb
                + 0.5 * ssd_gb 
                - 0.005 * price_rub
                ) stored   
            );
            
            """)

        #con.execute("DELETE FROM computers;")



main()

#ozon_parse()
