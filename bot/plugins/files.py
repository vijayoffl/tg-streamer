from telethon import Button
from telethon.events import NewMessage
from telethon.errors import MessageAuthorRequiredError, MessageNotModifiedError, MessageIdInvalidError
from telethon.tl.custom import Message
from secrets import token_hex
from bot import TelegramBot
from bot.config import Telegram, Server
from bot.modules.decorators import verify_user
from bot.modules.telegram import send_message, filter_files
from bot.modules.static import *
import logging


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@TelegramBot.on(NewMessage(incoming=True, func=filter_files))
@verify_user(private=True)
async def user_file_handler(event: NewMessage.Event | Message):
    try:
        # Generate a secret code
        #secret_code = token_hex(Telegram.SECRET_CODE_LENGTH)
        secret_code = token_hex(12)
        logger.info(f'Generated secret code: {secret_code}')
        
        # Update message text
        event.message.text = f'`{secret_code}`'
        
        # Send message
        message = await send_message(event.message)
        message_id = message.id
        
        # Log message ID
        logger.info(f'Message sent successfully with ID: {message_id}')
    
    except Exception as e:
        # Log any errors
        logger.error(f'Error in user_file_handler: {e}', exc_info=True)

    dl_link = f'{Server.BASE_URL}/dl/{message_id}?code={secret_code}'
    tg_link = f'{Server.BASE_URL}/file/{message_id}?code={secret_code}'
    deep_link = f'https://t.me/{Telegram.BOT_USERNAME}?start=file_{message_id}_{secret_code}'

    if (event.document and 'video' in event.document.mime_type) or event.video:
        stream_link = f'{Server.BASE_URL}/stream/{message_id}?code={secret_code}'
        await event.reply(
            message= MediaLinksText % {'dl_link': dl_link, 'tg_link': tg_link, 'tg_link': tg_link, 'stream_link': stream_link},
            buttons=[
                [
                    Button.url('Download', dl_link),
                    Button.url('Stream', stream_link)
                ],
                [
                    Button.url('Get File', deep_link),
                    Button.inline('Revoke', f'rm_{message_id}_{secret_code}')
                ]
            ]
        )
    else:
        await event.reply(
            message=FileLinksText % {'dl_link': dl_link, 'tg_link': tg_link},
            buttons=[
                [
                    Button.url('Download', dl_link),
                    Button.url('Get File', deep_link)
                ],
                [
                    Button.inline('Revoke', f'rm_{message_id}_{secret_code}')
                ]
            ]
        )

@TelegramBot.on(NewMessage(incoming=True, func=filter_files, forwards=False))
@verify_user()
async def channel_file_handler(event: NewMessage.Event | Message):
    secret_code = token_hex(Telegram.SECRET_CODE_LENGTH)
    event.message.text = f"`{secret_code}`"
    message = await send_message(event.message)
    message_id = message.id

    dl_link = f"{Server.BASE_URL}/dl/{message_id}?code={secret_code}"
    tg_link = f"{Server.BASE_URL}/file/{message_id}?code={secret_code}"

    if (event.document and "video" in event.document.mime_type) or event.video:
        stream_link = f"{Server.BASE_URL}/stream/{message_id}?code={secret_code}"

        try:
            await event.edit(
                buttons=[
                    [Button.url("Download", dl_link), Button.url("Stream", stream_link)],
                    [Button.url("Get File", tg_link)],
                ]
            )
        except (
            MessageAuthorRequiredError,
            MessageIdInvalidError,
            MessageNotModifiedError,
        ):
            pass
    else:
        try:
            await event.edit(
                buttons=[
                    [Button.url("Download", dl_link), Button.url("Get File", tg_link)]
                ]
            )
        except (
            MessageAuthorRequiredError,
            MessageIdInvalidError,
            MessageNotModifiedError,
        ):
            pass
