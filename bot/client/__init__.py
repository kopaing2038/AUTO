from typing import Union

from pyrogram import handlers, types

from .client import PatchedClient
from typing import AsyncGenerator, Optional, Union

async def resolve_listener(
    client: PatchedClient,
    update: Union[types.CallbackQuery, types.Message, types.InlineQuery, types.ChosenInlineResult],
):
    if isinstance(update, types.CallbackQuery):
        if update.message:
            key = f"{update.message.chat.id}:{update.message.id}"
        elif update.inline_message_id:
            key = update.inline_message_id
        else:
            return
    elif isinstance(update, (types.ChosenInlineResult, types.InlineQuery)):
        key = str(update.from_user.id)
    else:
        key = str(update.chat.id)  # type: ignore

    listener = client.listeners.get(key)

    if listener and not listener["future"].done():  # type: ignore
        if callable(listener["filters"]):
            if not await listener["filters"](client, update):
                update.continue_propagation()
        listener["future"].set_result(update)  # type: ignore
        update.stop_propagation()
    else:
        if listener and listener["future"].done():  # type: ignore
            client.remove_listener(key, listener["future"])


class Client(PatchedClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def start(self, *args, **kwargs):
        self.add_handler(handlers.CallbackQueryHandler(resolve_listener), group=-2)
        self.add_handler(handlers.InlineQueryHandler(resolve_listener), group=-2)
        self.add_handler(handlers.ChosenInlineResultHandler(resolve_listener), group=-2)
        self.add_handler(handlers.MessageHandler(resolve_listener), group=-2)
        await super().start(*args, **kwargs)


    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:  # type: ignore
        """Iterate through a chat sequentially.
        This convenience method does the same as repeatedly calling :meth:`~pyrogram.Client.get_messages` in a loop, thus saving
        you from the hassle of setting up boilerplate code. It is useful for getting the whole chat messages with a
        single call.
        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``):
                Identifier of the last message to be returned.

            offset (``int``, *optional*):
                Identifier of the first message to be returned.
                Defaults to 0.
        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        Example:
            .. code-block:: python
                for message in app.iter_messages("pyrogram", 1, 15000):
                    print(message.text)
        """
        current = offset

        while self.is_idling:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(
                chat_id, list(range(current, current + new_diff + 1))
            )
            for message in messages:  # type: ignore
                yield message
                current += 1
            await asyncio.sleep(10)
