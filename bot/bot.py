import telebot
import requests
import json
import os
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import sys

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')
    except:
        pass
    
    # Для логов с русскими именами пользователей
    if hasattr(sys.stdout, 'buffer'):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Логирование
log_handlers = [logging.StreamHandler()]
if not os.path.exists("logs"):
    os.makedirs("logs")
log_handlers.append(logging.FileHandler("logs/bot_main.log", encoding='utf-8'))

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# Токены и ключи
BOT_TOKEN = "6440647840:AAEZfv_z6W7-b_29rRbzMDrk_9W1wd3N6HA"
WEATHER_API_KEY = "9647f8586dfbab8b3776a8fa1fcb8539"

# Создаем бота с указанием таймаута
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# Логирование сообщений
def log_message(user_id, user_message, bot_response):
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"{user_id}.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - Пользователь: {user_message}\n")
            f.write(f"{timestamp} - Бот: {bot_response}\n\n")
    except Exception as e:
        logger.error(f"Ошибка при записи лога: {e}")

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    response = "Привет! Я бот погоды. Вот мои команды:\n" + \
               "/weather [город] - Погода через API\n" + \
               "/forecast [город] - Прогноз на 5 дней через API\n" + \
               "/yandex [город] - Погода с Яндекс.Погоды\n" + \
               "/gismeteo [город] - Погода с Gismeteo"
    
    bot.send_message(message.chat.id, response)
    log_message(user_id, "/start", response)

# Команда /weather - погода через API
@bot.message_handler(commands=['weather'])
def get_weather(message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        response = "Укажите город. Например: /weather Москва"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
        return
    
    city = command_parts[1]
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    try:
        weather_response = requests.get(url, timeout=10)
        weather_data = weather_response.json()
        
        if weather_data.get("cod") != 200:
            response = f"Не удалось найти город {city}"
            bot.send_message(message.chat.id, response)
            log_message(user_id, message.text, response)
            return
        
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        
        response = f"🌡 Погода в {city}:\n" + \
               f"Температура: {temp}°C\n" + \
               f"Описание: {description}\n" + \
               f"Влажность: {humidity}%"
        
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды: {e}")
        response = f"Ошибка при получении данных: {str(e)}"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)

# Команда /forecast - прогноз через API
@bot.message_handler(commands=['forecast'])
def get_forecast(message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        response = "Укажите город. Например: /forecast Москва"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
        return
    
    city = command_parts[1]
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
    
    try:
        forecast_response = requests.get(url, timeout=10)
        forecast_data = forecast_response.json()
        
        if forecast_data.get("cod") != "200":
            response = f"Не удалось найти город {city}"
            bot.send_message(message.chat.id, response)
            log_message(user_id, message.text, response)
            return
        
        response = f"Прогноз для {city}:\n\n"
        
        # Группируем по дням
        days = {}
        for item in forecast_data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in days:
                days[date] = []
            days[date].append(item)
        
        for date, items in list(days.items())[:3]:  # Только 3 дня
            temps = [item["main"]["temp"] for item in items]
            avg_temp = sum(temps) / len(temps)
            description = items[0]["weather"][0]["description"]
            
            response += f" {date}:\n" + \
                    f"Ср. температура: {avg_temp:.1f}°C\n" + \
                    f"Описание: {description}\n\n"
        
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
    except Exception as e:
        logger.error(f"Ошибка при запросе прогноза: {e}")
        response = f"Ошибка при получении данных: {str(e)}"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)

# Команда /yandex - скрапинг Яндекс.Погоды
@bot.message_handler(commands=['yandex'])
def get_yandex_weather(message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        response = "Укажите город. Например: /yandex Москва"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
        return
    
    city = command_parts[1]
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        url = f"https://yandex.ru/pogoda/{city.lower()}"
        
        # Ограничиваем количество перенаправлений
        response_html = requests.get(url, headers=headers, allow_redirects=True, timeout=10, max_redirects=5)
        
        if response_html.status_code != 200:
            response = f"Не удалось найти город {city} на Яндекс.Погоде"
            bot.send_message(message.chat.id, response)
            log_message(user_id, message.text, response)
            return
        
        soup = BeautifulSoup(response_html.text, 'html.parser')
        
        # Обновленные селекторы для Яндекс.Погоды
        selectors = [
            '.temp__value',
            '.fact__temp .temp__value', 
            '.fact__temp',
            '.temperature'
        ]
        temp_element = None
        for selector in selectors:
            temp_element = soup.select_one(selector)
            if temp_element:
                break
                
        desc_selectors = [
            '.link__condition',
            '.fact__condition',
            '.forecast__condition'
        ]
        desc_element = None
        for selector in desc_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                break
                
        feels_like_selectors = [
            '.temp__feels-like',
            '.fact__feels-like'
        ]
        feels_like_element = None
        for selector in feels_like_selectors:
            feels_like_element = soup.select_one(selector)
            if feels_like_element:
                break
        
        temp = temp_element.text if temp_element else "Н/Д"
        description = desc_element.text if desc_element else "Н/Д"
        feels_like = feels_like_element.text.replace('Ощущается как ', '') if feels_like_element else "Н/Д"
        
        response = f" Погода в {city} (Яндекс):\n" + \
                  f"Температура: {temp}\n" + \
                  f"Описание: {description}\n" + \
                  f"Ощущается как: {feels_like}"
        
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
    
    except Exception as e:
        logger.error(f"Ошибка при получении данных с Яндекс.Погоды: {str(e)}")
        response = f"Ошибка при получении данных: {str(e)}"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)

# Команда /gismeteo - скрапинг Gismeteo
@bot.message_handler(commands=['gismeteo'])
def get_gismeteo_weather(message):
    user_id = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        response = "Укажите город. Например: /gismeteo Москва"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
        return
    
    city = command_parts[1]
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        
        # Прямой доступ к погоде, минуя поиск
        city_encoded = city.lower().replace(' ', '-')
        direct_url = f"https://www.gismeteo.ru/weather-{city_encoded}/now/"
        
        try:
            # Сначала пробуем прямой доступ
            response_html = requests.get(direct_url, headers=headers, timeout=10)
            if response_html.status_code != 200:
                raise Exception("Город не найден напрямую")
                
            soup = BeautifulSoup(response_html.text, 'html.parser')
        except:
            # В случае ошибки используем поиск
            search_url = f"https://www.gismeteo.ru/search/{city}/"
            search_response = requests.get(search_url, headers=headers, timeout=10)
            
            if search_response.status_code != 200:
                response = f"Не удалось найти город {city} на Gismeteo"
                bot.send_message(message.chat.id, response)
                log_message(user_id, message.text, response)
                return
            
            search_soup = BeautifulSoup(search_response.text, 'html.parser')
            city_link = search_soup.select_one('.catalog-item a')
            
            if not city_link:
                response = f"Город {city} не найден на Gismeteo"
                bot.send_message(message.chat.id, response)
                log_message(user_id, message.text, response)
                return
            
            city_url = "https://www.gismeteo.ru" + city_link['href']
            
            # Получаем данные
            response_html = requests.get(city_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response_html.text, 'html.parser')
        
        # Список всех возможных селекторов
        temp_selectors = [
            '.unit_temperature_c', 
            '.weather-value',
            '.temp .value',
            '.tempvalue'
        ]
        
        desc_selectors = [
            '.description',
            '.weather-description',
            '.condition'
        ]
        
        humidity_selectors = [
            '.humidity .value',
            '.weather-humidity',
            '.humidity-value'
        ]
        
        # Находим первый работающий селектор для каждого элемента
        temp_element = None
        for selector in temp_selectors:
            temp_element = soup.select_one(selector)
            if temp_element:
                break
                
        desc_element = None
        for selector in desc_selectors:
            desc_element = soup.select_one(selector)
            if desc_element:
                break
                
        humidity_element = None
        for selector in humidity_selectors:
            humidity_element = soup.select_one(selector)
            if humidity_element:
                break
        
        temp = temp_element.text if temp_element else "Н/Д"
        description = desc_element.text.strip() if desc_element else "Н/Д"
        humidity = humidity_element.text + '%' if humidity_element else "Н/Д"
        
        response = f"🌤 Погода в {city} (Gismeteo):\n" + \
                  f"Температура: {temp}\n" + \
                  f"Описание: {description}\n" + \
                  f"Влажность: {humidity}"
        
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)
    
    except Exception as e:
        logger.error(f"Ошибка при получении данных с Gismeteo: {str(e)}")
        response = f"Ошибка при получении данных: {str(e)}"
        bot.send_message(message.chat.id, response)
        log_message(user_id, message.text, response)

def polling_with_retry():
    try:
        logger.info("Запуск бота в режиме polling...")
        bot.polling(none_stop=True, interval=1, timeout=20, long_polling_timeout=20, allowed_updates=["message"])
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        logger.info("Перезапуск через 10 секунд...")
        time.sleep(10)
        polling_with_retry()

if __name__ == "__main__":
    try:
        # Создаем директорию для логов
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        logger.info("Бот запущен")
        polling_with_retry()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
