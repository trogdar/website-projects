"""A server-side Flask app to parse POST requests from GroupMe."""
if __name__ == '__main__':
    from json import loads
    from multiprocessing import Process
    from typing import List, Union, Optional, Callable
    import asyncio
    import requests
    from flask import Flask, request

    from constants import WEBHOOK_URL


    app = Flask(__name__)


    @app.route('/', methods=['POST'])
    def index():
        """Method for base route."""
        message_object = loads(request.data)
        requests.post(
            WEBHOOK_URL, data={
                'username': message_object['name'],
                'content': message_object['text'],
                'avatar_url': message_object['avatar_url']
            }
        )
        return ''
    

    class WebProcess(Process):

        def __init__(self,
                    group=None,
                    target=None,
                    name=None,
                    args=(),
                    kwargs=None):
            super().__init__(group, target, name, args)
            self.loop: Optional[asyncio.AbstractEventLoop] = None
            self.stopped: Optional[asyncio.Event] = None
        

        def run(self):
            self.loop = asyncio.get_event_loop()
            self.stopped = asyncio.Event()
            self.loop.run_until_complete(app.run())