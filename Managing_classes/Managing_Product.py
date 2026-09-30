import asyncio
from Managing_classes.abstraction_for_classes import Managing_class
from Logger.logga import log
from Data_types.data_classes import Product
from Data_types.asyncfetch import AsyncFetcher
from typing import Optional
from Data.config import ConfigStorage


class Product_manager(Managing_class):

    @staticmethod
    def parse_json(item: dict, category_id: str) -> Optional[Product]:
        """Маппинг подтверждён реальным ответом products API (поля: plu, name,
        prices.regular/discount/cpd_promo_price, uom, property_clarification,
        rating, stock_limit, is_available, image_links)."""
        if not item:
            return None

        def _f(v):
            try:
                return float(v) if v is not None else None
            except (TypeError, ValueError):
                return None

        prices = item.get("prices") or {}
        rating = item.get("rating") or {}
        images = (item.get("image_links") or {}).get("small") or []

        return Product(
            product_id=str(item.get("plu", "")),
            name=item.get("name", ""),
            regular_price=_f(prices.get("regular")),
            discount_price=_f(prices.get("discount")),
            cpd_promo_price=_f(prices.get("cpd_promo_price")),
            category=category_id,
            uom=item.get("uom"),
            property_clarification=item.get("property_clarification"),
            rating=rating.get("rating_average"),
            rates_count=rating.get("rates_count"),
            stock_limit=_f(item.get("stock_limit")),
            is_available=item.get("is_available"),
            image_url=images[0] if images else None,
            raw=item,
        )

    @staticmethod
    async def get_products_for_category(fetcher: AsyncFetcher, store_id: str, category_id: str, limit: int = 30, max_pages: int = 50) -> list[Product]:
        Datan = ConfigStorage()
        url = Datan.PRODUCTS_API_TEMPLATE.format(store_id=store_id, category_id=category_id)
        products: list[Product] = []
        offset = 0
        for _ in range(max_pages):
            # Реальный ответ (см. пример) не содержит явного поля пагинации
            # (next/has_more/total) — только плоский список "products". Пробуем
            # offset; если сервер его игнорирует и возвращает те же товары
            # заново, здесь может понадобиться dedup или другой параметр
            # (проверьте, меняется ли список при разных offset).
            params = {
                "mode": "delivery",
                "include_restrict": "true",
                "order_by": "popularity",
                "limit": limit,
                "offset": offset,
            }
            data = await fetcher.fetch_json(url, params=params, headers=Datan.ORDERS_HEADERS)
            if not data:
                break
            items = data.get("products") or []
            if not items:
                break
            products.extend(p for p in (Product_manager.parse_json(item, category_id) for item in items) if p)
            if len(items) < limit:
                break
            offset += limit
        return products

    @staticmethod
    async def scrape(fetcher: AsyncFetcher, store_id: str, category_ids: list[str]) -> list[Product]:
        log.info("Собираю каталог магазина %s по %s категориям", store_id, len(category_ids))
        tasks = [Product_manager.get_products_for_category(fetcher, store_id, cat_id) for cat_id in category_ids]
        results = await asyncio.gather(*tasks)
        return [p for sub in results for p in sub]