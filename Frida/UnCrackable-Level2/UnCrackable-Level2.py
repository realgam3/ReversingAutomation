# -*- coding: utf-8 -*-
import frida
import codecs
from time import sleep


def on_message(message, data):
    print message, data


if __name__ == '__main__':
    device = frida.get_usb_device(2000)
    pid = device.spawn(["sg.vantagepoint.uncrackable2"])
    session = device.attach(pid)
    script = session.create_script(codecs.open("UnCrackable-Level2.js", encoding='utf-8').read())
    script.on('message', on_message)
    script.load()
    device.resume(pid)
    sleep(100)
    device.kill(pid)
