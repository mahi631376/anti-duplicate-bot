from database import (
    calculate_hash,
    exists_hash,
    exists_media,
    save_hash,
    save_media,
)


async def check_text(text: str):
    text_hash = calculate_hash(text)

    if await exists_hash(text_hash):
        return True

    await save_hash(text_hash, "text")
    return False


async def check_forward(message):
    # اگر پیام فورواردی متن داشته باشد
    if message.text:
        return await check_text(message.text)

    return False


async def check_photo(photo):
    media_id = photo.file_unique_id

    if await exists_media(media_id):
        return True

    await save_media(media_id, "photo")
    return False


async def check_document(document):
    media_id = document.file_unique_id

    if await exists_media(media_id):
        return True

    await save_media(media_id, "document")
    return False
