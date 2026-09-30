from Managing_classes.abstraction_for_classes import Managing_class
from Logger.logga import log
from Data_types.data_classes import Offer
from Data_types.asyncfetch import AsyncFetcher
from typing import Optional
from Data.config import ConfigStorage


class Offer_manager(Managing_class):
    @staticmethod
    def parse_json(item: dict) -> Optional[Offer]:
        """Маппинг подтверждён реальным ответом promo-offers API."""
        if not item:
            return None
        advert = item.get("advert") or {}
        return Offer(
            offer_id=item.get("slug", ""),
            title=item.get("title", ""),
            description=item.get("annonce"),
            image_url=item.get("preview"),
            valid_from=item.get("active_since"),
            valid_to=item.get("active_till"),
            external_link=item.get("external_link"),
            is_advert=advert.get("is_advert"),
            raw=item,
        )

    @staticmethod
    async def scrape_offers(fetcher: AsyncFetcher, promo_type: str = "mainpage_promotion", limit: int = 20) -> list[Offer]:
        Datan = ConfigStorage()
        # Реальный ответ — плоский {"offers": [...]}, без recognisable пагинации
        # на 5 элементах. Если понадобится больше типов акций, поищите в
        # DevTools другие значения "type" (не только mainpage_promotion).
        params = {"limit": limit, "web_version": "true", "type": promo_type}
        data = await fetcher.fetch_json(Datan.OFFERS_API_URL, params=params, headers=Datan.PUBLIC_HEADERS)
        if not data:
            return []
        items = data.get("offers") or []
        offers = [o for o in (Offer_manager.parse_json(item) for item in items) if o]
        log.info("Собрано %s акций (type=%s)", len(offers), promo_type)
        return offers