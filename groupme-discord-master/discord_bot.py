"""Discord-side message parsing and posting to GroupMe."""
if __name__ == '__main__':
    import json
    from os import path
    from sys import exit
    from io import BytesIO
    from random import randint
    from multiprocessing import Process
    from typing import List, Union, Optional, Callable
    import asyncio
    from discord.ext import commands
    from aiohttp import ClientSession
    from discord import Attachment, Message

    from constants import BOT_TOKEN, GROUPME_TOKEN, GROUPME_ID, CHANNEL_ID

    def get_prefix(
            bot_instance: commands.Bot, message: Message
        ) -> Callable[[commands.Bot, Message], list]:
            """Decide prefixes of the Bot."""
            prefixes = ['chat!', '>']
            return commands.when_mentioned_or(*prefixes)(bot_instance, message)


    bot = commands.Bot(command_prefix=get_prefix)


    @bot.event
    async def on_ready() -> None:
        """Called when the bot loads."""
        print('-------------\nBot is ready!\n-------------')


    @bot.event
    async def on_message(message: Message) -> None:
        """Called on each message sent in a channel."""
        if message.channel.id == CHANNEL_ID:
            if not message.author.bot:
                print(await DiscordProcess.send_message(message))
            elif message.content in DiscordProcess.sent_buffer:
                await message.delete()

    class DiscordProcess(Process):

        def __init__(self,
                    group=None,
                    target=None,
                    name=None,
                    args=(),
                    kwargs=None):
            super().__init__(group, target, name, args)
            self.loop: Optional[asyncio.AbstractEventLoop] = None
            self.stopped: Optional[asyncio.Event] = None
            self.endpoint = 'https://api.groupme.com/v3/bots/post'

            self.sent_buffer = []  # Buffer for webhook message deletions.
            dp.start()
        def run(self):
            self.loop = asyncio.get_event_loop()
            self.stopped = asyncio.Event()
            self.loop.run_until_complete(bot.run())



        async def post(
            self,
            session: ClientSession, url: str,
            payload: Union[BytesIO, dict], headers: Optional[dict] = None
        ) -> str:
            """Post data to a specified url."""
            async with session.post(url, data=payload) as response:
                return await response.text()

        async def send_message(self,message: Message) -> str:
            """Send a message to the group chat."""
            text = f'{message.author.display_name}: {message.content}'.strip()
            self.sent_buffer.append(text)
            if len(self.sent_buffer) > 10:
                self.sent_buffer.pop(0)
            payload = {
                'bot_id': GROUPME_ID,
                'text': f'{message.author.display_name}: {message.content}'
            }
            cdn = await self.process_attachments(message.attachments)
            if cdn is not None:
                payload.update({'picture_url': cdn})
            async with ClientSession() as session:
                return await self.post(session, self.endpoint, payload)


        async def process_attachments(self,attachments: List[Attachment]) -> str:
            """Process the attachments of a message and return GroupMe objects."""
            if not attachments:
                return
            attachment = attachments[0]
            url = 'https://image.groupme.com/pictures'
            if not attachment.filename.endswith(('jpeg', 'jpg', 'png', 'gif')):
                return
            extension = attachment.filename.partition('.')[-1]
            if extension == 'jpg':
                extension = 'jpeg'
            handler = BytesIO()
            await attachment.save(handler)
            headers = {
                'X-Access-Token': GROUPME_TOKEN,
                'Content-Type': f'image/{extension}'
            }
            async with ClientSession(headers=headers) as session:
                cdn = await self.post(session, url, handler.read())
                cdn = json.loads(cdn)['payload']['url']
            return cdn



