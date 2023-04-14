# import config
from aiogram import Bot, Dispatcher, executor, types
from doc_checking import check
from fixCorruptedPPTX import fix

# bot init
# bot = Bot(token = config.TOKEN)
TOKEN = "" # @docCheckerBot
bot = Bot(token = TOKEN)
dp = Dispatcher(bot)

ID_BOT = int(TOKEN.split(":")[0])


def split_messages(message):
    LIMIT = 4096
    while len(message) > LIMIT:
        message_breakpoint = message[0:LIMIT].rfind("\n")
        breakpoint_offset = 1
        if message_breakpoint > LIMIT or message_breakpoint == -1:
            message_breakpoint = message[0:LIMIT].rfind(" ")
            if message_breakpoint > LIMIT or message_breakpoint == -1:
                message_breakpoint = LIMIT
                breakpoint_offset = 0
        split = message[0 : message_breakpoint]
        yield split
        message = message[message_breakpoint + breakpoint_offset : ]
    if message:
        yield message


# documents
@dp.message_handler(content_types=["document"])
async def echo(message: types.Message):
    MB = 1024 * 1024
    try:
        if message.document.file_size < 100 * MB:
            doc_path = message.document.file_name
            await message.document.download(doc_path)
            fix(doc_path)
            outputText = check(doc_path)
            for each_message in split_messages(outputText):
                await message.answer(each_message, reply=True)
        else:
            await message.answer("Слишком большой файл", reply=True)
    except Exception as Error:
        await message.answer(Error, reply=True)


# run long-polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)