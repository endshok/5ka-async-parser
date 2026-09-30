import aiohttp
import asyncio
import json
from Logger.logga import log
from Data.config import ConfigStorage
from Data_types.asyncfetch import AsyncFetcher
from Managing_classes.Managing_Offer import Offer_manager
from Managing_classes.Managing_Product import Product_manager
from Managing_classes.Managing_Store import Store_manager
from dataclasses import asdict

async def main():
    Datan = ConfigStorage()
    async with aiohttp.ClientSession(headers=Datan.HEADERS) as session:
        fetcher = AsyncFetcher(session)

        # "Тёплый" заход на главную страницу — чтобы получить базовые
        # cookie, которые сайт может проверять (spid/spjs и т.п.). Если
        # API и без этого отвечает 200 — можно убрать этот шаг.
        await fetcher.fetch_text(f"{Datan.BASE_URL}/")

        stores = await Store_manager.scrape(fetcher)

        # Каталог собираем для первого найденного магазина — в реальном
        # прогоне замените на нужный store_id (sap_code) или переберите
        # все stores, если нужен каталог каждого магазина отдельно.
        store_id = stores[0].store_id if stores else "363H"

        products, offers = await asyncio.gather(
            Product_manager.scrape(fetcher, store_id, Datan.CATEGORY_IDS),
           Offer_manager.scrape(fetcher),
        )
    offers = [] if offers is None else offers
    with open("stores.json", "w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in stores], f, ensure_ascii=False, indent=2)

    with open("catalog.json", "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in products], f, ensure_ascii=False, indent=2)

    with open("offers.json", "w", encoding="utf-8") as f:
        json.dump([asdict(o) for o in offers], f, ensure_ascii=False, indent=2)

    log.info("Готово: магазинов=%s, товаров=%s, акций=%s", len(stores), len(products), len(offers))