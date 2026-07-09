import time
import board
import digitalio
import usb_hid

from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode


# =====================
# BUTTONS
# =====================

button_pins = [
    board.GP0,
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
]

buttons = []

for pin in button_pins:
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP
    buttons.append(button)


# =====================
# HID
# =====================

mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
consumer = ConsumerControl(usb_hid.devices)


# =====================
# ENCODER CLASS
# =====================

class Encoder:
    def __init__(self, clk_pin, dt_pin, sw_pin):
        self.clk = digitalio.DigitalInOut(clk_pin)
        self.clk.direction = digitalio.Direction.INPUT
        self.clk.pull = digitalio.Pull.UP

        self.dt = digitalio.DigitalInOut(dt_pin)
        self.dt.direction = digitalio.Direction.INPUT
        self.dt.pull = digitalio.Pull.UP

        self.sw = digitalio.DigitalInOut(sw_pin)
        self.sw.direction = digitalio.Direction.INPUT
        self.sw.pull = digitalio.Pull.UP

        self.last_clk = self.clk.value
        self.last_button = self.sw.value
        self.last_move = 0


    def update(self, clockwise, counterclockwise, press):
        current_clk = self.clk.value

        # Rotation detection
        if current_clk != self.last_clk:
            if self.dt.value != current_clk:
                clockwise()
            else:
                counterclockwise()

            time.sleep(0.002)

        self.last_clk = current_clk


        # Button press detection
        if self.last_button and not self.sw.value:
            press()

        self.last_button = self.sw.value



# =====================
# ENCODERS
# =====================

volume_encoder = Encoder(
    board.GP10,
    board.GP11,
    board.GP12
)


tab_encoder = Encoder(
    board.GP13,
    board.GP14,
    board.GP15
)


# =====================
# ACTIONS
# =====================

# Volume knob

def volume_up():
    consumer.send(
        ConsumerControlCode.VOLUME_INCREMENT
    )


def volume_down():
    consumer.send(
        ConsumerControlCode.VOLUME_DECREMENT
    )


def mic_mute():
    try:
        consumer.send(
            ConsumerControlCode.MICROPHONE_MUTE
        )
    except:
        print("Microphone mute unsupported")


# Browser knob

def next_tab():
    keyboard.press(
        Keycode.CONTROL,
        Keycode.TAB
    )
    keyboard.release_all()


def previous_tab():
    keyboard.press(
        Keycode.CONTROL,
        Keycode.SHIFT,
        Keycode.TAB
    )
    keyboard.release_all()


def close_tab():
    keyboard.press(
        Keycode.CONTROL,
        Keycode.W
    )
    keyboard.release_all()



# =====================
# START
# =====================

print("Chemistry Macro Pad Ready!")


# =====================
# MAIN LOOP
# =====================

while True:

    # Update encoders
    volume_encoder.update(
        volume_up,
        volume_down,
        mic_mute
    )

    tab_encoder.update(
        next_tab,
        previous_tab,
        close_tab
    )


    # Buttons
    for i, button in enumerate(buttons):

        if not button.value:

            print(f"Button {i+1} pressed")

            # Add macros here
            if i == 0:
                mouse.move(x=-35, y=0)

            elif i == 1:
                mouse.move(x=35, y=0)

            elif i == 2:
                mouse.move(x=0, y=-35)

            elif i == 3:
                mouse.move(x=0, y=35)


            time.sleep(0.15)  # debounce


    time.sleep(0.001)