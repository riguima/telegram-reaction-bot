from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from telegram_reaction_bot.database import db


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    phone_number: Mapped[str]


class Reaction(Base):
    __tablename__ = 'reactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[str]
    reaction_amount: Mapped[int]


Base.metadata.create_all(db)
