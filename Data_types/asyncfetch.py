import asyncio
import aiohttp
import json
from Logger.logga import log
from typing import Optional
from Data.config import ConfigStorage


class AsyncFetcher:
    def __init__(self, session: aiohttp.ClientSession):
        self.Datan = ConfigStorage()
        self.session = session
        self.semaphore = asyncio.Semaphore(self.Datan.CONCURRENCY_LIMIT)

    async def fetch_text(self, url: str, params: dict | None = None, headers: dict | None = None) -> Optional[str]:
        for attempt in range(1, self.Datan.MAX_RETRIES + 1):
            try:
                async with self.semaphore:
                    async with self.session.get(url, params=params, headers=headers, timeout=self.Datan.REQUEST_TIMEOUT) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        if resp.status == 404:
                            log.warning("404: %s", url)
                            return None
                        log.warning("Статус %s для %s (попытка %s/%s)", resp.status, url, attempt, self.Datan.MAX_RETRIES)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                log.warning("Ошибка запроса %s: %s (попытка %s/%s)", url, e, attempt, self.Datan.MAX_RETRIES)
            await asyncio.sleep(self.Datan.RETRY_DELAY * attempt)
        log.error("Не удалось получить %s после %s попыток", url, self.Datan.MAX_RETRIES)
        return None

    async def fetch_json(self, url: str, params: dict | None = None, headers: dict | None = None) -> Optional[dict]:
        """Многие подобные сайты отдают данные через внутренний JSON API
        (например /api/v1/stores). Если найдёте такой эндпоинт через
        DevTools, используйте этот метод вместо fetch_text + BeautifulSoup —
        это надёжнее и быстрее."""
        for attempt in range(1, self.Datan.MAX_RETRIES + 1):
            try:
                async with self.semaphore:
                    async with self.session.get(url, params=params, headers=headers, timeout=self.Datan.REQUEST_TIMEOUT) as resp:
                        if resp.status == 200:
                            return await resp.json(content_type=None)
                        log.warning("Статус %s для %s (попытка %s/%s)", resp.status, url, attempt, self.Datan.MAX_RETRIES)
            except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                log.warning("Ошибка запроса %s: %s (попытка %s/%s)", url, e, attempt, self.Datan.MAX_RETRIES)
            await asyncio.sleep(self.Datan.RETRY_DELAY * attempt)
        return None