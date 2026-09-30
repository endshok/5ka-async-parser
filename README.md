# Async Retail Parser (5ka)

Асинхронный парсер каталога товаров, акционных предложений и точек продаж сети «Пятёрочка».

## 🚀 Особенности и архитектура

* **Асинхронная архитектура:** Запросы выполняются через `aiohttp` с ограничением конкурентности через `asyncio.Semaphore` для предотвращения блокировок.
* **Отказоустойчивость:** Реализован механизм автоматических повторных попыток (Retries) с задержками при сетевых ошибках и таймаутах.
* **Модульность:** Разделение ответственности (Single Responsibility Principle) — абстрактные менеджеры данных, отдельные структуры через `dataclass` и централизованный конфиг.
* **Логирование:** Встроенное отслеживание статусов ответов API и ошибок через `logging`.

## 🛠 Технологический стек

* Python 3.14
* Asyncio / aiohttp
* Dataclasses
* Configparser

## 📦 Запуск проекта

1. Клонируйте репозиторий:
   ```bash
    git clone [https://github.com/endshok/5ka-async-parser.git](https://github.com/endshok/5ka-async-parser.git)
    cd 5ka-async-parser
2. Введите команду для установки зависимостей
    ```bash
    pip install -r requirements.txt
    #или просто pip install aiohttp
3. Запустите парсер:
    ```bash
   python Main/run.py