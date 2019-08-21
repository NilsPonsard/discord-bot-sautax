import threading
import queue
import discord


class Threaded_request(threading.Thread):
    def __init__(self, function):
        self.function = function
        self.q = queue.Queue()
        self.args = []
        return super().__init__()

    def run(self):
        """
        the function must return 4 things (can be None) : content, embed, file,files
        """
        self.q.put(self.function(*self.args))
        # return super().run()

    async def setup(self, client, message, *args):
        self.__init__(self.function)
        self.args = args
        self.start()
        sent_message = await message.channel.send(content="processing ...")
        await self.task(client, message, sent_message)

    async def task(self, client, message, sent_message):
        if self.q.empty():
            client.loop.create_task(
                self.task(client, message,    sent_message))
        else:
            q_out = self.q.get()
            if q_out == None:
                return
            else:
                (content, embed, file, files) = q_out
                await sent_message.delete()
                await message.channel.send(content=content, embed=embed, file=file, files=files)
