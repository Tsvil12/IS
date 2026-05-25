# Погодный бот — техническая документация

## Как работает бот

### 1. Библиотеки

| Библиотека | Зачем |
|------------|-------|
| `pytelegrambotapi` | Работа с Telegram Bot API |
| `requests` | HTTP-запросы к API OpenWeatherMap и сайтам |
| `BeautifulSoup` | Парсинг HTML (Яндекс, Gismeteo) |
| `logging` | Логирование |
| `datetime` | Временные метки в логах |

---

### 2. Команды и их механизм

| Команда | Источник | Тип |
|---------|----------|-----|
| `/weather` | OpenWeatherMap API | API |
| `/forecast` | OpenWeatherMap API | API |
| `/yandex` | Яндекс.Погода | Scraping |
| `/gismeteo` | Gismeteo | Scraping |

---

### 3. Логирование

- **`logs/bot_main.log`** — ошибки и события бота
- **`logs/{user_id}.log`** — диалог пользователя с ботом

Функция записи лога:
```python
def log_message(user_id, user_message, bot_response):
    with open(f"logs/{user_id}.log", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} - Пользователь: {user_message}\n")
        f.write(f"{timestamp} - Бот: {bot_response}\n\n")
```

---

### 4. API (OpenWeatherMap)

**Эндпоинты:**
- Текущая погода: `api.openweathermap.org/data/2.5/weather`
- Прогноз: `api.openweathermap.org/data/2.5/forecast`

**Параметры:**
- `q={city}` — город
- `appid={API_KEY}` — ключ
- `units=metric` — градусы Цельсия
- `lang=ru` — описание на русском

---

### 5. Scraping (парсинг)

**Яндекс.Погода:**
```
https://yandex.ru/pogoda/{city}
```
Селекторы:
- Температура: `.temp__value`, `.fact__temp`
- Описание: `.link__condition`, `.fact__condition`

**Gismeteo:**
```
https://www.gismeteo.ru/weather-{city}/now/
```
Селекторы:
- Температура: `.unit_temperature_c`, `.weather-value`
- Описание: `.description`
- Влажность: `.humidity .value`

---

### 6. Токены и ключи

В коде:
```python
BOT_TOKEN = "6440647840:AAEZfv_z6W7-b_29rRbzMDrk_9W1wd3N6HA"
WEATHER_API_KEY = "9647f8586dfbab8b3776a8fa1fcb8539"
```

---

