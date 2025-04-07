import sounddevice as sd
import re

device_name = "Choice"
for i, device in enumerate(sd.query_devices()):
    print(device)
    if device_name in device['name'] and device['max_input_channels'] > 0:
        tmp = device['name']
        tmp = "Yundea 1076: USB Audio (hw:1,0)"
        hw_idx = re.findall(r"\(hw:(\d+,\d+)", tmp)
        # hw_idx = re.match(r"hell(w+)", "hello world")
        print(hw_idx[0])
        print(f"找到索引: {hw_idx} - {device_name}")
        break