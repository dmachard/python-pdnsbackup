import logging
import aiohttp
import aiohttp.web

logger = logging.getLogger("pdnsbackup")

# init web router
router = aiohttp.web.RouteTableDef()

async def setup(loop, cfg):
    """setup the web api"""
    # init the web application
    app = aiohttp.web.Application()
    app.add_routes(router)
    app["cfg"] = cfg

    # run api server
    listen_address = (cfg["web_listen_ip"], cfg["web_listen_port"])
    try:
        srv = await loop.create_server(app.make_handler(access_log=None), *listen_address)
    except OSError as e:
        logger.error( "webapi: %s" % e)
        return None
    logger.debug("webapi: listening on %s:%s" % listen_address )
    return srv
