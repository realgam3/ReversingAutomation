import frida


def on_message(message, data):
    print message


# Find Frida server on USB Device (Mobile)
device = frida.get_usb_device(1000)
# Open APP On Pause State And Attach To It
pid = device.spawn([raw_input("Package Name:")])
session = device.attach(pid)
# Load Script And Add Message Callback
script = session.create_script(open('DynamicHooks.js').read())
script.on('message', on_message)
script.load()
# Resume App
device.resume(pid)
# Wait For User Input To End The Script
raw_input('Press enter to continue...')
