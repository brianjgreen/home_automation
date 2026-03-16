#
# sudo -E env PATH=${PATH} python3 docker_test.py
#
# List shairport-sync containers by name, room, and USB DAC
#

import docker

client = docker.from_env()

all_containers = client.containers.list(all)
print(all_containers)
for container in all_containers:
    # print(container.attrs["Config"])
    if "mikebrady/shairport-sync" in container.attrs["Config"]["Image"]:
        room = container.attrs["Config"]["Cmd"][1]
        usb_dongle = container.attrs["Config"]["Cmd"][-1]
        print(f"{container.name} {container.status} {room} {usb_dongle}")

print(client.images.list())
