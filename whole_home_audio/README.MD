# Control Whole Home Audio

- Docker containers for each room (USB DAC for each channel on amplifier)
- Using latest shairport-sync which supports AirPlay2 (can select several speakers and sync)

```bash
sudo docker pull mikebrady/shairport-sync
````

```bash
sudo docker run -d --restart unless-stopped --net host --device /dev/snd mikebrady/shairport-sync -a DenSystem -- -d hw:Set
```

Rooms not already attached to a dedicated RPi Zero W are on USB hubs connected to
an X86 Linux box.
Example output from `aplay -l` showing USB headphone DACs:

```bash
- card 2: Set [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 3: Set_1 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 4: Set_2 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 5: Set_3 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 6: Set_4 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 7: Set_5 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 8: Set_6 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
- card 9: Set_7 [C-Media USB Headphone Set], device 0: USB Audio [USB Audio]
  - Subdevices: 1/1
  - Subdevice #0: subdevice #0
```
