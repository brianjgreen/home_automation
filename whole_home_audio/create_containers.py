#
# sudo -E env PATH=${PATH} python3 create_container.py
#
# sudo docker run -d --restart unless-stopped --net host --device /dev/snd \
#     mikebrady/shairport-sync -a DenSystem -- -d hw:Set
#
# Create shairport-sync containers for each room by USB DAC connection
#
import docker

shairport_image_name_tag = "mikebrady/shairport-sync:latest"
client = docker.from_env()

images = client.images.list()
print(images)

shairport_image = client.images.get(shairport_image_name_tag)
print(shairport_image)

# change these to match your room names and USB DAC connections
connections = {
    "hw:Set": "MasterBath",
    "hw:Set_1": "GuestBed",
    "hw:Set_2": "Bedroom1",
    "hw:Set_3": "Office1",
    "hw:Set_4": "Office2",
    "hw:Set_5": "Pub",
    "hw:Set_6": "Bedroom2",
    "hw:Set_7": "MasterBed",
}


def create_new_container(room, usb_dev):
    return client.containers.create(
        shairport_image_name_tag,
        detach=True,
        restart_policy={"Name": "unless-stopped"},
        network="host",
        devices=[
            "/dev/snd",
        ],
        command=f'-a {room} -- -d "{usb_dev}"',
    )


def get_containers():
    shairport_containers = {}
    all_containers = client.containers.list(all)
    print(all_containers)
    for container in all_containers:
        # print(container.attrs["Config"])
        if "mikebrady/shairport-sync" in container.attrs["Config"]["Image"]:
            room = container.attrs["Config"]["Cmd"][1]
            usb_dongle = container.attrs["Config"]["Cmd"][-1]
            print(f"{container.name} {container.status} {room} {usb_dongle}")
            if room in shairport_containers:
                print(f"DUPLICATE CONTAINER! {room}")
            else:
                shairport_containers[room] = usb_dongle
    return shairport_containers


shairport_containers = get_containers()
for usb_dev, room in connections.items():
    print(f"{room} => {usb_dev}")
    if room in shairport_containers:
        print(f"Room {room} already has a container!")
    else:
        new_container = create_new_container(room, usb_dev)
        print(new_container)
