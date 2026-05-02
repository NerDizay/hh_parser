from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import logging
from environs import Env

# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Инициализация environs
env = Env()
env.read_env()


def login(driver):
    """
    Функция для входа на hh.ru (если требуется авторизация).
    На hh.ru авторизация может быть необходима для доступа к некоторым данным.
    """
    driver.get('https://hh.ru/')
    
    # Ждем появления кнопки входа
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-qa='header-login-btn']"))
    )
    login_button.click()
    
    # Получаем данные из переменных окружения
    email = env.str("HH_EMAIL", "")
    password = env.str("HH_PASSWORD", "")
    
    if email and password:
        # Ввод логина и пароля
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        logging.info("Авторизация выполнена.")
    else:
        logging.warning("Страница входа открыта. Данные для входа не найдены в переменных окружения (HH_EMAIL, HH_PASSWORD).")


def main(driver):
    """
    Основная функция для парсинга hh.ru
    """
    login(driver)
    
    # Пример парсинга: поиск вакансий по запросу
    driver.get('https://hh.ru/search/vacancy?text=python')
    
    # Ждем загрузки результатов
    vacancies = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.vacancy-serp-item"))
    )
    
    logging.info(f"Найдено вакансий: {len(vacancies)}")
    
    for i, vacancy in enumerate(vacancies[:5]):  # Выводим первые 5 вакансий
        title = vacancy.find_element(By.CSS_SELECTOR, "span").text
        logging.info(f"{i+1}. {title}")


def init_driver():
    """
    Инициализация драйвера браузера с настройками из .env
    """
    # Читаем настройку headless из .env (по умолчанию True)
    is_headless = env.bool("HEADLESS", True)
    
    options = webdriver.ChromeOptions()
    if is_headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


if __name__ == "__main__":
    driver = None
    try:
        driver = init_driver()
        main(driver)
    except Exception as e:
        logging.critical(f"Критическая ошибка в точке входа: {e}")
    finally:
        if driver:
            driver.quit()
