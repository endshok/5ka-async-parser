from dataclasses import dataclass, field, asdict
from typing import Optional

@dataclass
class Store:
    store_id: str
    address: str
    city: Optional[str] = None
    working_hours: Optional[str] = None
    phone: Optional[str] = None
    has_delivery: Optional[bool] = None
    has_24h_delivery: Optional[bool] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    raw: Optional[dict] = None  # сырой JSON на случай, если понадобятся другие поля


@dataclass
class Product:
    product_id: str          # plu
    name: str
    regular_price: Optional[float] = None   # prices.regular
    discount_price: Optional[float] = None  # prices.discount (обычная скидка)
    cpd_promo_price: Optional[float] = None  # prices.cpd_promo_price (цена по акции/карте)
    category: Optional[str] = None
    uom: Optional[str] = None                # "шт" / "кг"
    property_clarification: Optional[str] = None  # "200 г", "Цена за 1 кг" и т.п.
    rating: Optional[float] = None
    rates_count: Optional[int] = None
    stock_limit: Optional[float] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    raw: Optional[dict] = None


@dataclass
class Offer:
    offer_id: str        # slug
    title: str
    description: Optional[str] = None  # annonce
    image_url: Optional[str] = None    # preview (относительный путь на media-хосте)
    valid_from: Optional[str] = None   # active_since
    valid_to: Optional[str] = None     # active_till
    external_link: Optional[str] = None
    is_advert: Optional[bool] = None
    raw: Optional[dict] = None