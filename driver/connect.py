import asyncio
import subprocess
import sys

import requests

from pymobiledevice3.exceptions import NoDeviceConnectedError, TunneldConnectionError
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.tunneld.api import TUNNELD_DEFAULT_ADDRESS, get_tunneld_device_by_udid


async def get_usbmux_lockdownclient():
    while True:
        try:
            lockdown = await create_using_usbmux()
        except NoDeviceConnectedError:
            print("请连接设备后按回车...")
            input()
        else:
            break

    while lockdown.all_values.get("PasswordProtected"):
        await lockdown.close()
        print("请解锁设备后按回车...")
        input()
        lockdown = await create_using_usbmux()

    return lockdown


def get_version(lockdown):
    return lockdown.product_version


async def get_developer_mode_status(lockdown):
    return await lockdown.get_developer_mode_status()


async def reveal_developer_mode(lockdown):
    await AmfiService(lockdown).reveal_developer_mode_option_in_ui()


def start_tunneld_if_needed():
    try:
        response = requests.get(f"http://{TUNNELD_DEFAULT_ADDRESS[0]}:{TUNNELD_DEFAULT_ADDRESS[1]}", timeout=0.5)
        if response.json():
            return
    except requests.RequestException:
        pass

    subprocess.run(
        ["pkill", "-9", "-f", "[p]ymobiledevice3 remote tunneld"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [sys.executable, "-m", "pymobiledevice3", "remote", "tunneld", "--daemonize"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


async def get_tunneld_rsd(udid: str, timeout=45):
    deadline = asyncio.get_running_loop().time() + timeout
    start_tunneld_if_needed()

    while True:
        try:
            rsd = await get_tunneld_device_by_udid(udid)
        except TunneldConnectionError:
            rsd = None

        if rsd is not None:
            return rsd

        if asyncio.get_running_loop().time() >= deadline:
            raise NoDeviceConnectedError("未能通过 tunneld 建立 iOS Remote Service Discovery 连接")

        await asyncio.sleep(1)
