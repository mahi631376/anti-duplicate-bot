import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import (
    WARNING_TEXT,
    WARNING_DELETE_AFTER,
)

from duplicate import (
    check_text,
    check_forward,
    check_photo,
    check_document,
)

from database import (
    init_database,
    clean_old_messages,
)

BOT_TOKEN = "YOUR_BOT_TOKEN"
async def is_admin(update: Update):

    member = await update.effective_chat.get_member(
        update.effective_user.id
    )

    return member.status in (
        "administrator",
        "creator",
    )


async def delete_warning(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
):

    await asyncio.sleep(WARNING_DELETE_AFTER)

    try:
        await context.bot.delete_message(
            chat_id,
            message_id,
        )

    except Exception:
        pass
      async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if update.effective_chat.type not in (
        "group",
        "supergroup",
    ):
        return

    if await is_admin(update):
        return

    message = update.effective_message

    duplicate = False
    if message.forward_origin:
        duplicate = await check_forward(message)

    elif message.text:
        duplicate = await check_text(
            message.text
        )

    elif message.photo:
        duplicate = await check_photo(
            message.photo[-1]
        )

    elif message.document:
        duplicate = await check_document(
            message.document
        )
          if duplicate:

        await message.delete()

        warning = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=WARNING_TEXT,
            reply_to_message_id=None,
        )

        asyncio.create_task(
            delete_warning(
                context,
                warning.chat.id,
                warning.message_id,
            )
        )

        return
async def main():

    await init_database()

    await clean_old_messages()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle_message,
        )
    )

    print("Bot Started...")

    await app.run_polling()


if __name__ == "__main__":

    asyncio.run(main())
