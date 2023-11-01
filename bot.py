import pyromod
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from telegram_reaction_bot.config import config
from telegram_reaction_bot.database import Session
from telegram_reaction_bot.models import Account, Reaction

bot = Client(
    config['BOT_USERNAME'],
    api_id=config['API_ID'],
    api_hash=config['API_HASH'],
    bot_token=config['BOT_TOKEN'],
)


@bot.on_message(
    filters.command('start') & filters.chat(config['ADMIN_USERNAME'])
)
async def start(_, message):
    await message.reply(
        'Escolha uma opção:',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        'Adicionar Conta', callback_data='add_account'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Remover Conta', callback_data='remove_account'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Contas', callback_data='show_accounts'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Adicionar reação', callback_data='add_reaction'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Remover reação', callback_data='remove_reaction'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Reações', callback_data='show_reactions'
                    )
                ],
            ]
        ),
    )


@bot.on_callback_query(filters.regex(r'add_account'))
async def add_account(client, callback_query):
    username = await callback_query.message.chat.ask(
        'Digite o nome de usúario da conta'
    )
    phone_number = await callback_query.message.chat.ask(
        'Digite o número de telefone da nova conta, formato +5511999999999'
    )
    account_app = Client(
        username.text,
        api_id=config['API_ID'],
        api_hash=config['API_HASH'],
    )
    await account_app.connect()
    try:
        sent_code = await account_app.send_code(phone_number.text)
        code = await callback_query.message.chat.ask(
            'Digite o código de verificação com qualquer letra no começo, exemplo: a97780'
        )
        await account_app.sign_in(
            phone_number.text, sent_code.phone_code_hash, code.text[1:]
        )
        with Session() as session:
            account = Account(
                username=username.text, phone_number=phone_number.text
            )
            session.add(account)
            session.commit()
        await callback_query.message.reply('Conta adicionada')
    except BadRequest:
        await callback_query.message.reply(
            'Número de telefone ou código inválido'
        )
    except SessionPasswordNeeded:
        await callback_query.message.reply(
            'Desabilite a verificação de duas etapas da sua conta'
        )
    await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'^remove_account$'))
async def remove_account(client, callback_query):
    with Session() as session:
        options = []
        for account in session.scalars(select(Account)).all():
            options.append(
                [
                    InlineKeyboardButton(
                        f'{account.username} - {account.phone_number}',
                        callback_data=f'remove_account:{account.id}',
                    )
                ]
            )
        if options:
            await callback_query.message.reply(
                'Escolha uma conta para remover:',
                reply_markup=InlineKeyboardMarkup(options),
            )
        else:
            await callback_query.message.reply('Nenhuma conta adicionada')
            await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'remove_account:\d+'))
async def remove_account_action(client, callback_query):
    with Session() as session:
        account_id = int(callback_query.data.split(':')[-1])
        account = session.get(Account, account_id)
        session.delete(account)
        session.commit()
    await callback_query.message.reply('Conta removida')
    await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'show_accounts'))
async def show_accounts(client, callback_query):
    with Session() as session:
        options = []
        for account in session.scalars(select(Account)).all():
            options.append(
                [
                    InlineKeyboardButton(
                        f'{account.username} - {account.phone_number}',
                        callback_data=account.username,
                    )
                ]
            )
        if options:
            await callback_query.message.reply(
                'Contas:', reply_markup=InlineKeyboardMarkup(options)
            )
        else:
            await callback_query.message.reply('Nenhuma conta adicionada')
        await start(client, callback_query.message)


@bot.on_callback_query(filters.regex('add_reaction'))
async def add_reaction(client, callback_query):
    with Session() as session:
        group = await callback_query.message.chat.ask(
            'Digite o arroba, ID ou Link de convite do grupo'
        )
        reaction_amount = await callback_query.message.chat.ask(
            'Digite a quantidade de reações'
        )
        reaction = Reaction(
            group=group.text,
            reaction_amount=int(reaction_amount.text),
        )
        session.add(reaction)
        session.commit()
    await callback_query.message.reply('Reação adicionada')
    await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'^remove_reaction$'))
async def remove_reaction(client, callback_query):
    with Session() as session:
        options = []
        for reaction in session.scalars(select(Reaction)).all():
            options.append(
                [
                    InlineKeyboardButton(
                        f'{reaction.group} - {reaction.reaction_amount}',
                        callback_data=f'remove_reaction:{reaction.id}',
                    )
                ]
            )
        if options:
            await callback_query.message.reply(
                'Escolha uma reação para remover:',
                reply_markup=InlineKeyboardMarkup(options),
            )
        else:
            await callback_query.message.reply('Nenhuma reação adicionada')
            await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'remove_reaction:\d+'))
async def remove_reaction_action(client, callback_query):
    with Session() as session:
        reaction_id = int(callback_query.data.split(':')[-1])
        reaction = session.get(Reaction, reaction_id)
        session.delete(reaction)
        session.commit()
    await callback_query.message.reply('Reação removida')
    await start(client, callback_query.message)


@bot.on_callback_query(filters.regex(r'show_reactions'))
async def show_reactions(client, callback_query):
    with Session() as session:
        options = []
        for reaction in session.scalars(select(Reaction)).all():
            options.append(
                [
                    InlineKeyboardButton(
                        f'{reaction.group} - {reaction.reaction_amount}',
                        callback_data=reaction.group,
                    )
                ]
            )
        if options:
            await callback_query.message.reply(
                'Reações:', reply_markup=InlineKeyboardMarkup(options)
            )
        else:
            await callback_query.message.reply('Nenhuma reação adicionada')
        await start(client, callback_query.message)


if __name__ == '__main__':
    bot.run()
