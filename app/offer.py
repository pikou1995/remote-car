import json
from car import car
from video import RTCVideoTrack
from audio import RTCAudioTrack
from peerconnection import PeerConnectionFactory, pcs
from aiohttp import web
from aiortc import RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
# from aiortc.mediastreams import  VideoStreamTrack

# Factory to create peerConnections depending on the iceServers set by user
pc_factory = PeerConnectionFactory()

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type'])
    pc = pc_factory.create_peer_connection()
    # options = {'framerate': '30', 'video_size': '640x480'}
    # webcam = MediaPlayer('/dev/video0', format='v4l2', options=options)
    # relay = MediaRelay()
    pcs.add(pc)
    # pc.addTrack(relay.subscribe(webcam.video))
    # Add local media
    pc.addTrack(RTCVideoTrack())
    pc.addTrack(RTCAudioTrack())

    @pc.on('datachannel')
    def on_datachannel(channel):
        @channel.on('message')
        def on_message(msg):
            if msg == 'w':
                car.forward()
            elif msg == 'a':
                car.left()
            elif msg == 's':
                car.backward()
            elif msg == 'd':
                car.right()
            elif msg == 'i':
                car.servo.up()
            elif msg == 'j':
                car.servo.left()
            elif msg == 'k':
                car.servo.down()
            elif msg == 'l':
                car.servo.right()
            else:
                car.stop()
            car.delay_stop(0.3)

    @pc.on('iceconnectionstatechange')
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == 'failed':
            await pc.close()
            pcs.discard(pc)
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.Response(
        content_type='application/json',
        text=json.dumps({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }))
