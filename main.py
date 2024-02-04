import asyncio
import enum
import logging
import re

import phonenumbers
from loguru import logger
from pyrogram import Client
from pyrogram.types import Chat

from config import chat_name_list, api_id, api_hash, phone_number
from database import create_conn, get, new, TypeFeedback
from pkg.logger import Logger


app = Client(
    name="my_account",
    api_id=api_id,
    api_hash=api_hash,
    phone_number=phone_number,
)

for chat_name in chat_name_list:
    with app:
        try:
            app.join_chat(chat_name)
        except Exception as e:
            logger.error(f"Не удалось присоединиться к чату {chat_name}: {e}")


async def get_history(app):
    pool = await create_conn()
    for chat_name in chat_name_list:
        async for message in app.get_chat_history(chat_name):
            await parse_comment(message.text, pool)


@app.on_message()
async def my_handler(client, message):
    chat: Chat = message.chat
    if chat.username not in chat_name_list:
        return
    logger.info(f"Message from {chat.username}: {message.text}")
    await parse_comment(message.text)


async def parse_comment(text, pool=None):
    if text is None:
        return
    phone, ok = await parse_phone_by_text(text)
    if not ok:
        return
    logger.info(f"Phone: {phone}")
    description = await parse_description_by_text(text)
    await update_database(phone, description, pool)


async def update_database(phone, description, pool=None):
    if pool is None:
        pool = await create_conn()
    feedback = await get(pool, phone, description)
    if feedback is None:
        await new(pool, phone, description)


async def parse_phone_by_text(text):
    text = text.replace('o', '0').replace('о', '0').replace('O', '0').replace('О', '0').replace('+8', '+7')
    pattern = r'(\+?[78])[ \-]?\(?(?:(\d{3})\)?[ \-]?(\d{3})[ \-]?(\d{2})[ \-]?(\d{2})|\d{1}[ \-]?(\d{3})[ \-]?(\d{3})[ \-]?(\d{2})[ \-]?(\d{2}))'
    match = re.search(pattern, text)
    if match:
        if match.group(2):
            phone = '7' + match.group(2) + match.group(3) + match.group(4) + match.group(5)
        else:
            phone = '7' + match.group(6) + match.group(7) + match.group(8) + match.group(9)

        return phone, True

    for match in phonenumbers.PhoneNumberMatcher(text, "RU"):
        phone_number = phonenumbers.parse(match.raw_string, "RU")
        phone = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        phone = phone[1:] if phone.startswith('+') else phone
        return phone, True

    return False, False


async def parse_description_by_text(text):
    text = re.sub(r'#\w+', '', text).strip()
    text = re.sub(r'@\w+', '', text).strip()
    text = re.sub(r'\b(?:Телеграмм|БОТ)\b', '', text).strip()
    text = text.strip()
    text = re.sub(r'\n\s*\n', '\n', text)

    return text


# async def main():
#     async with Client(
#             name="prima_acc",
#             api_id=api_id,
#             api_hash=api_hash,
#             phone_number=phone_number,
#     ) as app:
#         await get_history(app)


if __name__ == '__main__':
    log = Logger(
        log_level="info",
        log_dir_name="logs",
        info_log_path="logs/info.log",
        debug_log_path="logs/debug.log",
    )
    log.setup_logger()
    logger.debug("Debug mode is on")
    # asyncio.run(main())
    app.run()
