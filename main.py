#!/usr/bin/python3
import mido
from pynput import keyboard

device_name = ""
push_key = None
inverted = False

try:
  from config import device_name,push_key,inverted
  print("Loading from config.py")
except:
  print("Select your Configuration")
  input_names = mido.get_input_names()
  input_devices = []
  # Looping logic as get_input_names returns duplicated entries
  for name in input_names:
    if name not in input_devices:
      input_devices.append(name)
      print(f'{len(input_devices)}. {name}')
  selected=0
  while True:  
    try:
      selected = int(input("Choose pedal device (negative number for reversed polarity): "))
    except:
      continue
    if selected < 0:
      selected = -selected
      inverted=True
    selected = selected-1
    if selected >= 0 and selected < len(input_devices):
      break
  device_name = input_devices[selected]    

  # Select the push-to-talk key
  print("Press Key that will be used for push-to-talk")
  def on_press(key):
    global push_key
    try:
      print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
      print('special key {0} pressed'.format(key))
    push_key = key
    return False

  listener = keyboard.Listener(
    on_press=on_press)
  listener.start()
  while push_key == None:
    pass
  listener.join(0.1)

# Detect if pedal (cc64) is pressed or lifted and act accordingly
with mido.open_input(device_name) as inport:
  spoof_keyboard = keyboard.Controller()
  for msg in inport:
    if msg.is_cc(64):
      talking = False
      if msg.value > 64:
        talking = True
      if inverted:
        talking = not talking
      if talking:
        spoof_keyboard.press(push_key)
        print("Talking...")
      else:
        spoof_keyboard.release(push_key)
        print("Silenced")