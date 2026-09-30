import asyncio
from Logger.logga import log
from Managing_classes.abstraction_for_classes import Managing_class
from Data_types.data_classes import Store
from Data_types.asyncfetch import AsyncFetcher
from Data.config import ConfigStorage


class Store_manager(Managing_class):

    @staticmethod
    def parse_json(item: dict) -> Store:
        """Разбирает один магазин из ответа /orders/v1/orders/stores/.
        Поля ниже подтверждены скриншотом Response; если в реальном JSON
        есть другие поля (например id, latitude/longitude, working_hours,
        phone) — допишите их сюда, весь сырой объект также сохраняется в raw.
        """
        return Store(
            store_id=str(item.get("sap_code") or item.get("id") or ""),
            address=item.get("shop_address", ""),
            city=item.get("store_city"),
            working_hours=item.get("working_hours"),  # уточнить точное имя поля
            phone=item.get("phone"),
            has_delivery=item.get("has_delivery"),
            has_24h_delivery=item.get("has_24h_delivery"),
            latitude=item.get("latitude") or item.get("lat"),
            longitude=item.get("longitude") or item.get("lon"),
            raw=item,
        )

    @staticmethod
    async def scrape( fetcher: AsyncFetcher, points: list[tuple[float, float]] | None = None) -> list[Store]:
        """points — список (lon, lat) точек, вокруг которых искать магазины.
        Судя по эндпоинту, это поиск "магазины рядом с точкой", а не полный
        список по всей сети — поэтому для покрытия многих городов нужно
        пройтись по нескольким координатам (центр каждого города/района) и
        объединить результаты, убрав дубликаты по sap_code.
        """
        Datan = ConfigStorage()
        points = points or [(Datan.DEFAULT_LON, Datan.DEFAULT_LAT)]

        async def _one(lon: float, lat: float) -> list[Store]:
            data = await fetcher.fetch_json(Datan.STORES_API_URL, params={"lon": lon, "lat": lat}, headers=Datan.ORDERS_HEADERS)
            if not data:
                return []
            # Структура ответа могла бы быть списком или объектом с полем
            # "results"/"items" — обрабатываем оба варианта на всякий случай.
            items = data if isinstance(data, list) else data.get("results") or data.get("items") or []
            return [Store_manager.parse_json(item) for item in items]

        results = await asyncio.gather(*(_one(lon, lat) for lon, lat in points))
        all_stores = [s for sub in results for s in sub]

        # Дедупликация по store_id
        seen = set()
        unique_stores = []
        for s in all_stores:
            if s.store_id and s.store_id not in seen:
                seen.add(s.store_id)
                unique_stores.append(s)

        log.info("Найдено %s уникальных магазинов", len(unique_stores))
        return unique_stores