import signal
import logging
import coloredlogs
import os

import console_utils
from driver import location

from pymobiledevice3.cli.remote import RemoteServiceDiscoveryService
from pymobiledevice3.cli.developer import DvtSecureSocketProxyService

from init import init
from init import tunnel
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



def main():
    # set level
    logger = logging.getLogger(__name__)
    coloredlogs.install(level=logging.INFO)
    logger.setLevel(logging.INFO)
    if debug:
        logger.setLevel(logging.DEBUG)
        coloredlogs.install(level=logging.DEBUG)
    console_utils.disable_quick_edit(logger)

    init.init()
    logger.info("init done")

    # start the tunnel in another process
    logger.info("starting tunnel")
    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    process, address, port = tunnel.tunnel()
    signal.signal(signal.SIGINT, original_sigint_handler)
    logger.info("tunnel started")
    try:
        logger.debug(f"tunnel address: {address}, port: {port}")

        # get route
        loc = route.get_route()
        logger.info(f"got route from {config.config.routeConfig}")


        with RemoteServiceDiscoveryService((address, port)) as rsd:
            with DvtSecureSocketProxyService(rsd) as dvt:
                location_simulation = location.create_simulation(dvt)
                if config.config.lowPriority:
                    console_utils.set_below_normal_priority(logger)
                try:
                    print(f"已开始模拟跑步，速度大约为 {config.config.v} m/s")
                    print("会无限循环，按 Ctrl+C 退出")
                    print("请勿直接关闭窗口，否则无法还原正常定位")
                    run.run(
                        location_simulation,
                        loc,
                        config.config.v,
                        dt=config.config.locationUpdateInterval,
                        min_distance=config.config.minLocationDistance,
                        randomize=config.config.randomizeRoute,
                        cache_route=config.config.cacheRoute,
                        speed_variation=config.config.speedVariation,
                    )
                except KeyboardInterrupt:
                    logger.debug("get KeyboardInterrupt (inner)")
                    logger.debug(f"Is process alive? {process.is_alive()}")
                finally:
                    logger.debug(f"Is process alive? {process.is_alive()}")
                    logger.debug("Start to clear location")
                    location.clear_location(location_simulation)
                    logger.info("Location cleared")


    except KeyboardInterrupt:
        logger.debug("get KeyboardInterrupt (outer)")
    finally:
        # stop the tunnel process
        logger.debug(f"Is process alive? {process.is_alive()}")
        logger.debug("terminating tunnel process")
        process.terminate()
        logger.info("tunnel process terminated")
        print("Bye")
    

    
if __name__ == "__main__":
    main()
