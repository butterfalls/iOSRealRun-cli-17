import logging
import coloredlogs
import os
import asyncio
import signal

from driver import connect, location

from pymobiledevice3.services.dvt.instruments.dvt_provider import DvtProvider
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation

from init import init
from init import route

import run

import config


debug = os.environ.get("DEBUG", False)

# set logging level
coloredlogs.install(level=logging.INFO)
logging.getLogger('wintun').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('quic').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('zeroconf').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.cache').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.cache.pickle').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('parso.python.diff').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('humanfriendly.prompts').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('blib2to3.pgen2.driver').setLevel(logging.DEBUG if debug else logging.WARNING)
logging.getLogger('urllib3.connectionpool').setLevel(logging.DEBUG if debug else logging.WARNING)



async def main():
    # set level
    logger = logging.getLogger(__name__)
    coloredlogs.install(level=logging.INFO)
    logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    device = await init.init()
    logger.info("init done")

    logger.info("connecting to tunneld")
    rsd = await connect.get_tunneld_rsd(device["udid"])
    logger.info("tunneld connected")
    try:
        # get route
        loc = route.get_route()
        logger.info(f"got route from {config.config.routeConfig}")

        async with DvtProvider(rsd) as dvt:
            async with LocationSimulation(dvt) as location_simulation:
                print(f"已开始模拟跑步，速度大约为 {config.config.v} m/s")
                print("会无限循环，按 Ctrl+C 退出")
                print("请勿直接关闭窗口，否则无法还原正常定位")
                try:
                    await run.run_async(location_simulation, loc, config.config.v, stop_event=stop_event)
                finally:
                    logger.debug("Start to clear location")
                    await location.clear_location(location_simulation)
                    logger.info("Location cleared")
    finally:
        await rsd.close()
        print("Bye")
    

    
if __name__ == "__main__":
    asyncio.run(main())
