#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import sys
from signal import signal, SIGINT
import asyncio
import aioxmpp
import aioxmpp.dispatcher


class Textpuffer:
    """
    A simple jabber client that prints out what it receives. This is meant
    to be used as a share-to-pc program. One can share text, especially links,
    with the connected jabber account. That text then is printed out at the
    pc that runs this python program.
    """

    def __init__(self, jid, password, receive_from):
        """
        Initialize the class by setting JID and password. Adds a dispatcher to
        receive messages from the defined account.
        @param jid: the jabber ID of the buffers account
        @param password: the password of the buffers jabber account
        @param receiveFrom: the jabber ID of the account that's allowed to
        send messages to this buffer
        """
        self.running = False
        self.receive_from = receive_from
        self.client = aioxmpp.PresenceManagedClient(
            aioxmpp.JID.fromstr(jid), aioxmpp.make_security_layer(password))
        message_dispatcher = self.client.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher)
        message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT, aioxmpp.JID.fromstr(receive_from),
            self.receive)
        self.loop = asyncio.get_event_loop()

    def start(self):
        """
        Set self.running to True and start the event loop.
        """
        self.running = True
        self.loop.run_until_complete(self.run())

    async def run(self):
        """
        Run the program. That means connecting, then sending a message to the
        account that can send text to this buffer, signaling that this buffer
        is now available.
        After that an infinite loop is started so the program can receive
        messages. This loop can be broken when self.running is set to false.
        """
        async with self.client.connected() as stream:
            msg = aioxmpp.Message(
                to=aioxmpp.JID.fromstr(self.receive_from),
                type_=aioxmpp.MessageType.CHAT)
            msg.body[None] = "Ready to receive now!"
            await self.client.send(msg)

            while self.running:
                await asyncio.sleep(10)

            msg = aioxmpp.Message(
                to=aioxmpp.JID.fromstr(self.receive_from),
                type_=aioxmpp.MessageType.CHAT)
            msg.body[None] = "Shutting down!"
            await self.client.send(msg)

            sys.exit(0)

    def stop(self, signal_received, frame):
        """
        Set running variable to False. This causes the main loop in run()
        to break.
        @param signal_received:
        @param frame:
        """
        self.running = False

    def receive(self, message):
        """
        Print out the bare messages body if it has any.
        @param message: the received message
        """
        if not message.body:
            return
        else:
            print(message.body.any())


def main(argv):
    """
    Initializes with the first three commandline arguments and starts it.
    Registers the SIGINT signal to call Textpuffer.stop() to end program
    when CTRL+C is pressed.
    """
    tp = Textpuffer(argv[1], argv[2], argv[3])
    signal(SIGINT, tp.stop)
    tp.start()


if __name__ == "__main__":
    main(sys.argv)
