import asyncio
import threading
import requests
from bs4 import BeautifulSoup
import httpx
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.request import HTTPXRequest
from telegram.error import RetryAfter
import signal

# Your bot token and channel details
TELEGRAM_BOT_TOKEN = '7312860580:AAHtGBvjSwt-r5CjDFTkKKAZFCS1WSV6UF0'
TELEGRAM_CHANNEL_CHAT_ID = -1002210529449
CHANNEL_URL = 'https://t.me/s/basejumpnewtokens'

# List of interesting developer addresses
top_creators = [
    "0x22724bA2C8c01B56aeD3c1727f620b61a2273e40",
    # Add other addresses here
]

# List to store seen tokens
seen_tokens = set()
all_addresses_accepted = True

# Initialize the bot with a custom request timeout
class CustomHTTPXRequest(HTTPXRequest):
    def __init__(self):
        super().__init__()
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))

bot = Bot(token=TELEGRAM_BOT_TOKEN, request=CustomHTTPXRequest())

# Command handlers
async def start(update: Update, context: CallbackContext) -> None:
    """
    Responds to the /start command.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("Received /start command")
    if update.message:
        await update.message.reply_text('Hello! This bot is working! /help')
    elif update.channel_post:
        await update.channel_post.reply_text('Hello! This bot is working! /help')

async def help_command(update: Update, context: CallbackContext) -> None:
    """
    Responds to the /help command.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("Received /help command")
    help_text = (
        "/start - Test the bot\n"
        "/add <address> - Add an address to the list of top creators\n"
        "/list - Show all top creator addresses\n"
        "/delete <address> - Remove an address from the list of top creators\n"
        "/help - Show this help"
    )
    if update.message:
        await update.message.reply_text(help_text)
    elif update.channel_post:
        await update.channel_post.reply_text(help_text)

async def add(update: Update, context: CallbackContext) -> None:
    """
    Responds to the /add command.
    Adds an address to the list of top creators if it doesn't already exist.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("Received /add command")
    if context.args:
        address = context.args[0]
        if address not in top_creators:
            top_creators.append(address)
            response = f'Address added: {address}'
        else:
            response = f'Address already exists: {address}'
    else:
        response = 'Usage: /add <address>'
    
    if update.message:
        await update.message.reply_text(response)
    elif update.channel_post:
        await update.channel_post.reply_text(response)

async def list_addresses(update: Update, context: CallbackContext) -> None:
    """
    Responds to the /list command.
    Displays all top creator addresses.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("Received /list command")
    if top_creators:
        addresses = '\n'.join(top_creators)
        response = f'Top creator addresses:\n{addresses}'
    else:
        response = 'No addresses added.'
    
    if update.message:
        await update.message.reply_text(response)
    elif update.channel_post:
        await update.channel_post.reply_text(response)

async def delete(update: Update, context: CallbackContext) -> None:
    """
    Responds to the /delete command.
    Removes an address from the list of top creators if it exists.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("Received /delete command")
    if context.args:
        address = context.args[0]
        if address in top_creators:
            top_creators.remove(address)
            response = f'Address removed: {address}'
        else:
            response = f'Address not found: {address}'
    else:
        response = 'Usage: /delete <address>'
    
    if update.message:
        await update.message.reply_text(response)
    elif update.channel_post:
        await update.channel_post.reply_text(response)

async def error_handler(update: Update, context: CallbackContext) -> None:
    """
    Handles errors occurring during update processing.
    Uses update.message.reply_text for private/group messages and update.channel_post.reply_text for channel posts.
    """
    print("An error occurred")
    try:
        if update.message:
            await update.message.reply_text('An error occurred. Please try again later.')
        elif update.channel_post:
            await update.channel_post.reply_text('An error occurred. Please try again later.')
    except RetryAfter as e:
        print(f"Flood control exceeded. Retry in {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        await error_handler(update, context)  # Retry the handler after the wait

# Channel post handler for commands
async def handle_channel_post(update: Update, context: CallbackContext) -> None:
    """
    Manually process commands in channel posts using if-elif statements.
    This ensures commands are handled correctly regardless of where they are received.
    """
    if update.channel_post:
        message_text = update.channel_post.text

        # Manually process commands in channel posts
        if message_text.startswith("/start"):
            await start(update, context)
        elif message_text.startswith("/help"):
            await help_command(update, context)
        elif message_text.startswith("/add"):
            await add(update, context)
        elif message_text.startswith("/list"):
            await list_addresses(update, context)
        elif message_text.startswith("/delete"):
            await delete(update, context)

# Function to fetch and parse messages
def fetch_messages(url):
    """
    Fetch messages from the provided URL and return a BeautifulSoup object.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def parse_messages(soup):
    """
    Parse messages from the BeautifulSoup object and extract token information.
    """
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
        
        # Extract developer address from links
        for link in links:
            if 'profile?address=' in link['href']:
                dev_address = link['href'].split('profile?address=')[1]
                token_info['dev_profile_link'] = link['href']
                token_info['dev_address'] = dev_address

        # Extract name, symbol, and goal
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

        # Extract links
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
    """
    Sends a formatted message with token information to the specified Telegram channel.
    Handles RetryAfter exceptions for flood control.
    """
    message = (
        f"🚀 <b>{token_info['name']} / {token_info['symbol']}</b>\n"
        f"Goal: {token_info['goal']} ETH\n\n"
        f"<b>Links:</b>\n"
        f"<a href='{token_info['buy_link']}'>Buy</a> | "
        f"<a href='{token_info['dev_profile_link']}'>Dev profile</a> | "
        f"<a href='{token_info['dev_basescan_link']}'>Dev Basescan</a> | "
        f"<a href='{token_info['chart_link']}'>Chart</a>\n\n"
        f"<b>Developer Address:</b> {token_info['dev_address']}\n\n"
        f"<i>/help</i>"
    )
    print(f"Sending new token info to channel: {token_info['name']} / {token_info['symbol']}")
    try:
        await bot.send_message(chat_id=TELEGRAM_CHANNEL_CHAT_ID, text=message, parse_mode='HTML')
    except RetryAfter as e:
        print(f"Flood control exceeded. Retry in {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        await send_message_to_channel(token_info)  # Retry sending the message after the wait

async def process_messages():
    """
    Continuously fetch and process messages from the channel URL every 0.2 seconds.
    """
    while True:
        soup = fetch_messages(CHANNEL_URL)
        if soup:
            token_infos = parse_messages(soup)
            for token_info in token_infos:
                await send_message_to_channel(token_info)
        await asyncio.sleep(0.2)  # Wait 0.2 seconds before fetching messages again

# Function to run the bot
def run_bot():
    """
    Configures and starts the Telegram bot, adding command handlers and error handler.
    """
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers for private and group messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("list", list_addresses))
    application.add_handler(CommandHandler("delete", delete))

    # Add an error handler
    application.add_error_handler(error_handler)

    # Add a handler for channel posts
    application.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

    # Start the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling())

# Main function to run the bot and message processing concurrently
async def main():
    """
    Runs the bot in a separate thread and processes messages concurrently in the main thread.
    """
    # Run the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Process messages in the main thread
    await process_messages()

# Signal handler for clean exit
def signal_handler(sig, frame):
    """
    Handles exit signals (SIGINT, SIGTERM) to gracefully shut down the program.
    """
    print("Received exit signal, shutting down gracefully...")
    loop = asyncio.get_event_loop()
    loop.stop()

if __name__ == '__main__':
    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"Runtime error: {e}")
