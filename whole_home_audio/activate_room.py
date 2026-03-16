#
# sudo -E env PATH=${PATH} python3 activate_room.py
#
# Airplay(2) gets confused if you run several instances of shairport with
# differnt port numbers on the same box.
# The iOS device will only see one shairport-sync client per IP address.
#
# Pick a room to connect to the shairport-sync and start that container.
# Stop the running container for a different room, if active.
# Only run one shairport-sync instance per IP address.
#

import argparse

import docker

client = docker.from_env()


def get_containers(client):
    container_state = {}
    for container in client.containers.list(all):
        # print(container.attrs)
        if "mikebrady/shairport-sync" in container.attrs["Config"]["Image"]:
            room = container.attrs["Config"]["Cmd"][1]
            usb_dongle = container.attrs["Config"]["Cmd"][-1]
            # print(f"{container.name} {container.status} {room} {usb_dongle}")
            state = False
            if container.attrs["State"]["Running"]:
                state = True
            active = "NOT Connected"
            if state:
                active = "ACTIVE"
            print(f"{room} in {container.name} on {usb_dongle} is {active}")
            container_state[room] = (container.name, state)

    return container_state


container_state = get_containers(client)
# print(container_state)
print(f"Rooms: {list(container_state.keys())}")

parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument("room", nargs="?", default=None)
args = parser.parse_args()
# print(args.room)

if args.room:
    if args.room in container_state:
        name, state = container_state[args.room]
        if state:
            print(f"{args.room} (container {name}) is already active.")
        else:
            for conn_name, conn_state in container_state.values():
                if conn_state:
                    print(f"Stopping container {conn_name}...")
                    stop_container = client.containers.get(conn_name)
                    stop_container.stop()
            print(f"Starting container {name}...")
            start_container = client.containers.get(name)
            start_container.start()
    else:
        print(f"{args.room} is not a known room name.")
