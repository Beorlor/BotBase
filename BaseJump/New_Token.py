import requests
from bs4 import BeautifulSoup
import asyncio
import httpx
from telegram import Bot
from telegram.request import HTTPXRequest

# URL du canal Telegram (version web)
channel_url = 'https://t.me/s/basejumpnewtokens'

# Contrôle si toutes les adresses sont acceptées ou seulement celles dans top_creators
all_addresses_accepted = True

# Liste des adresses de développeurs intéressantes
top_creators = [
    "0x22724bA2C8c01B56aeD3c1727f620b61a2273e40",
    # Ajoutez d'autres adresses ici
]

# Liste pour stocker les tokens déjà vus
seen_tokens = set()

# Votre token de bot
TELEGRAM_BOT_TOKEN = '7312860580:AAHtGBvjSwt-r5CjDFTkKKAZFCS1WSV6UF0'
# ID de chat de votre canal
TELEGRAM_CHANNEL_CHAT_ID = -1002210529449

# Initialisation du bot avec un délai personnalisé pour les requêtes
class CustomHTTPXRequest(HTTPXRequest):
    def __init__(self):
        super().__init__()
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))

bot = Bot(token=TELEGRAM_BOT_TOKEN, request=CustomHTTPXRequest())

def fetch_messages(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def parse_messages(soup):
    messages = soup.find_all('div', {'class': 'tgme_widget_message_text'})
    token_infos = []

    for message in messages:
        text = message.get_text(separator=' ').strip()
        links = message.find_all('a')
        dev_address = None
        token_info = {
            "name": None,
            "symbol": None,
            "goal": None,
            "dev_address": None,
            "buy_link": None,
            "dev_profile_link": None,
            "dev_basescan_link": None,
            "chart_link": None
        }
        
        # Extraire l'adresse du développeur des liens
        for link in links:
            if 'profile?address=' in link['href']:
                dev_address = link['href'].split('profile?address=')[1]
                token_info['dev_profile_link'] = link['href']
                token_info['dev_address'] = dev_address

        # Extraire le nom, le symbole et l'objectif
        parts = text.split('Goal:')
        if len(parts) > 1:
            name_symbol_part = parts[0].strip()
            goal_part = parts[1].strip()

            if '🚀' in name_symbol_part:
                name_symbol_part = name_symbol_part.split('🚀')[1].strip()
                name_symbol_split = name_symbol_part.split('/')
                token_info['name'] = name_symbol_split[0].strip()
                token_info['symbol'] = name_symbol_split[1].strip()
            
            token_info['goal'] = goal_part.split(' ')[0].strip()

        # Extraire les liens
        for link in links:
            if 'Buy' in link.text:
                token_info['buy_link'] = link['href']
            elif 'Dev profile' in link.text:
                token_info['dev_profile_link'] = link['href']
            elif 'Dev Basescan' in link.text:
                token_info['dev_basescan_link'] = link['href']
            elif 'Chart' in link.text:
                token_info['chart_link'] = link['href']
        
        if dev_address and (all_addresses_accepted or dev_address in top_creators):
            token_id = f"{token_info['name']}_{token_info['symbol']}_{token_info['dev_address']}"
            if token_id not in seen_tokens:
                seen_tokens.add(token_id)
                token_infos.append(token_info)
                print(f"New match found: {token_info}\n\n\n")
    return token_infos

async def send_message_to_channel(token_info):
    message = (
        f"🚀 <b>{token_info['name']} / {token_info['symbol']}</b>\n"
        f"Goal: {token_info['goal']} ETH\n\n"
        f"<b>Links:</b>\n"
        f"<a href='{token_info['buy_link']}'>Buy</a> | "
        f"<a href='{token_info['dev_profile_link']}'>Dev profile</a> | "
        f"<a href='{token_info['dev_basescan_link']}'>Dev Basescan</a> | "
        f"<a href='{token_info['chart_link']}'>Chart</a>\n\n"
        f"<b>Developer Address:</b> {token_info['dev_address']}"
    )
    await bot.send_message(chat_id=TELEGRAM_CHANNEL_CHAT_ID, text=message, parse_mode='HTML')

async def process_messages():
    soup = fetch_messages(channel_url)
    if soup:
        token_infos = parse_messages(soup)
        for token_info in token_infos:
            await send_message_to_channel(token_info)

async def main():
    while True:
        await process_messages()
        await asyncio.sleep(0.5)  # Attendre de récupérer les messages à nouveau

if __name__ == '__main__':
    asyncio.run(main())
