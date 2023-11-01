import random

from pyrogram import filters, idle
from pyrogram.client import Client
from pyrogram.errors import UserAlreadyParticipant
from sqlalchemy import select

from telegram_reaction_bot.config import config
from telegram_reaction_bot.database import Session
from telegram_reaction_bot.models import Account, Reaction

EMOJIS = [
    '👏',
    '❤️',
    '🤩',
    '🏆',
    '👍',
    '🤯',
    '🎉',
    '🥳',
    '🍾',
    '🔥',
    '😍',
    '🥰',
    '😎',
    '🙏',
    '❤️',
    '‍',
    '🔥',
    '💯',
    '⚡',
    '🤝',
    '😘',
]

admin_app = Client(
    config['ADMIN_USERNAME'],
    api_id=config['API_ID'],
    api_hash=config['API_HASH'],
)

with Session() as session:
    apps = [
        Client(
            account.username,
            api_id=config['API_ID'],
            api_hash=config['API_HASH'],
        )
        for account in session.scalars(select(Account)).all()
    ]


if __name__ == '__main__':
    admin_app.start()
    for app in apps:
        app.start()

        @app.on_message(~filters.private)
        async def send_reaction(_, message):
            chat = await admin_app.get_chat(message.chat.id)
            with Session() as session:
                for reaction in session.scalars(select(Reaction)).all():
                    if reaction.group in [chat.username, str(chat.id), chat.invite_link]:
                        try:
                            await app.get_chat(message.chat.id)
                        except ValueError:
                            await app.join_chat(chat.invite_link)
                        reactions_count = 0
                        if message.reactions:
                            for reaction in message.reactions.reactions:
                                reactions_count += reaction.count
                        if reactions_count < reaction.reaction_amount:
                            await message.react(emoji=random.choice(EMOJIS))
    idle()
    for app in apps:
        app.stop()
    admin_app.stop()
