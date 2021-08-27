#!/usr/bin/env python3

from RPi import GPIO
from offer import offer
from peerconnection import pcs
import asyncio
import os
import platform
import sys
from time import sleep
from aiohttp import web
from aiohttp_basicauth import BasicAuthMiddleware


async def index(request):
    content = open(os.path.join(ROOT, 'client/index.html'), 'r').read()
    return web.Response(content_type='text/html', text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, 'client/client.js'), 'r').read()
    return web.Response(content_type='application/javascript', text=content)


async def on_shutdown(app):
    GPIO.cleanup()
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)


def checkDeviceReadiness():
    if not os.path.exists('/dev/video0') and platform.system() == 'Linux':
        print('Video device is not ready')
        print('Trying to load bcm2835-v4l2 driver...')
        os.system('bash -c "modprobe bcm2835-v4l2"')
        sleep(1)
        sys.exit()
    else:
        print('Video device is ready')


if __name__ == '__main__':
    checkDeviceReadiness()

    ROOT = os.path.dirname(__file__)

    auth = []
    if 'username' in os.environ and 'password' in os.environ:
        print('\n#############################################################')
        print('Authorization is enabled.')
        print('Your balenaCam is password protected.')
        print('#############################################################\n')
        auth.append(BasicAuthMiddleware(
            username=os.environ['username'], password=os.environ['password']))

    # app = web.Application(middlewares=auth)
    app = web.Application()
    app.on_shutdown.append(on_shutdown)

    app.router.add_get('/', index)
    app.router.add_get('/client.js', javascript)
    app.router.add_post('/offer', offer)
    web.run_app(app, port=8080)
