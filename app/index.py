#!/usr/bin/env python3

from car import car
from RPi import GPIO
from offer import offer
from peerconnection import pcs
import asyncio
import os
import platform
import sys
from time import sleep
from aiohttp import web
import aiohttp
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


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)  # 等待websocket连接

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            elif msg.data == 'w':
                car.forward()
            elif msg.data == 'a':
                car.left()
            elif msg.data == 's':
                car.backward()
            elif msg.data == 'd':
                car.right()
            elif msg.data == 'i':
                car.servo.up()
            elif msg.data == 'j':
                car.servo.left()
            elif msg.data == 'k':
                car.servo.down()
            elif msg.data == 'l':
                car.servo.right()
            else:
                car.stop()
            car.delay_stop(0.3)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


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
    app.router.add_route('*', '/car', websocket_handler)
    web.run_app(app, port=8080)
