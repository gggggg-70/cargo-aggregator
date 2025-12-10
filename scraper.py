
import requests, time
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent":"CargoSiteBot/1.0 (+https://example.com)"}

def can_fetch(url, user_agent="*"):
    # very simple checker: fetch robots.txt for domain and look for Disallow lines
    try:
        from urllib.parse import urlparse, urljoin
        parsed = urlparse(url)
        robots = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")
        r = requests.get(robots, headers=HEADERS, timeout=5)
        if r.status_code != 200:
            return True
        txt = r.text.lower()
        # naive check
        if "disallow: /" in txt:
            return False
        return True
    except Exception as e:
        return True

def search_della_ati(query):
    # query example: "Алматы-Астана" or "Москва-Казань"
    results = []
    # parsers/della_parser.py
import re
from bs4 import BeautifulSoup

class DellaParser(BaseParser):
    async def parse_list_page(self, page: int) -> List[CargoAd]:
        url = f"{self.base_url}/грузоперевозки?page={page}"
        
        async with self.session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }) as response:
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        ads = []
        
        # Селекторы нужно определить через анализ сайта
        items = soup.select('.cargo-item, .order-item, .ad-item')
        
        for item in items:
            try:
                # Извлечение данных
                title_elem = item.select_one('.title, h3, .cargo-title')
                route_elem = item.select_one('.route, .path, .cities')
                
                if not title_elem or not route_elem:
                    continue
                
                # Парсинг маршрута "Москва → Санкт-Петербург"
                route_text = route_elem.text.strip()
                cities = re.split(r'[-–→>]', route_text)
                loading_city = cities[0].strip() if len(cities) > 0 else ''
                unloading_city = cities[1].strip() if len(cities) > 1 else ''
                
                # Поиск цены
                price_elem = item.select_one('.price, .cost, .sum')
                price = None
                currency = 'KZT'
                
                if price_elem:
                    price_text = price_elem.text.strip()
                    # Извлечение чисел из строки
                    numbers = re.findall(r'[\d\s]+', price_text.replace(' ', ''))
                    if numbers:
                        price = float(numbers[0].replace(' ', ''))
                        # Определение валюты
                        if '₸' in price_text or 'тг' in price_text.lower():
                            currency = 'KZT'
                        elif '$' in price_text or 'usd' in price_text.lower():
                            currency = 'USD'
                        elif '€' in price_text or 'eur' in price_text.lower():
                            currency = 'EUR'
                        elif '₽' in price_text or 'руб' in price_text.lower():
                            currency = 'RUB'
                
                ad = CargoAd(
                    source='della',
                    external_id=item.get('data-id', ''),
                    title=title_elem.text.strip(),
                    loading_city=loading_city,
                    unloading_city=unloading_city,
                    cargo_type=self._extract_cargo_type(item),
                    weight=self._extract_weight(item),
                    volume=self._extract_volume(item),
                    price=price,
                    currency=currency,
                    loading_date=self._extract_date(item),
                    contact_info={},
                    created_at='',
                    url=self._extract_url(item)
                )
                ads.append(ad)
                
            except Exception as e:
                self.logger.error(f"Ошибка парсинга элемента: {e}")
        
        return ads
    
    def _extract_cargo_type(self, item) -> str:
        # Логика определения типа груза
        pass
    
    def _extract_weight(self, item) -> float:
        # Логика извлечения веса
        pass
    
    def _extract_volume(self, item) -> float:
        # Логика извлечения объема
        pass
    
    def _extract_date(self, item) -> str:
        # Логика извлечения даты
        pass
    
    def _extract_url(self, item) -> str:
        # Логика извлечения URL
        pass
    # Example 2: search on ati.su (demo)
    ati_url = f"https://ati.su/search/?q={query}"
    if can_fetch(ati_url):
        try:
            r = requests.get(ati_url, headers=HEADERS, timeout=10)
            time.sleep(2)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True)[:10]:
                    title = a.get_text().strip()
                    link = a["href"]
                    if title:
                        results.append({"source":"ati", "title":title, "link":link})
        except Exception as e:
            print("ati error", e)
    return results
