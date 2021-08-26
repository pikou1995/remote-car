var primaryPeerConnection = null;
var backupPeerConnection = null;
var vfdIntervalId = null;
var state = 0;

window.onbeforeunload = function () {
  if (primaryPeerConnection !== null) {
    primaryPeerConnection.close();
  }
};

function attachStreamToVideoElement(pc, videoElem) {
  console.log('Attaching stream...');
  var srcStream = new MediaStream();
  pc.getReceivers().forEach(receiver => {
    srcStream.addTrack(receiver.track);
  })
  videoElem.srcObject = srcStream;
}

function peerConnectionGood(pc) {
  return ((pc.iceConnectionState === 'connected' || pc.iceConnectionState === 'completed'));
}

function peerConnectionBad(pc) {
  return ((pc.iceConnectionState === 'disconnected' || pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'closed'));
}

function hideAllContainers() {
  document.getElementById('spinner-container').style.display = 'none';
  document.getElementById('video-container').style.display = 'none';
  document.getElementById('fail-container').style.display = 'none';
  document.getElementById('mjpeg-container').style.display = 'none';
}

function showContainer(kind) {
  hideAllContainers();
  if (kind === 'video') {
    document.getElementById('video-container').style.display = 'block';
  } else if (kind === 'fail') {
    document.getElementById('fail-container').style.display = 'initial';
  } else if (kind === 'mjpeg') {
    document.getElementById('mjpeg-container').style.display = 'block';
  } else {
    console.error('No container that is kind of: ' + kind);
  }
}

function createNewPeerConnection() {
  var pc = new RTCPeerConnection();
  var isVideoAttached = false;
  new Promise(function (resolve, reject) {
    function mainIceListener() {
      console.warn(pc.iceConnectionState);
      if (peerConnectionBad(pc)) {
        if (state === 0) {
          //this means webrtc connection is not possible
          alert('webrtc connection is not possible')
        }
        if (state !== 2) {
          showContainer('fail');
        }
      }
      if (peerConnectionGood(pc)) {
        if (!isVideoAttached) {
          if (state === 0) {
            state = 1;
          }
          isVideoAttached = true;
          attachStreamToVideoElement(pc, document.getElementById('video'));
          cleanup();
          // startVideoFreezeDetection(pc);
        }
        showContainer('video');
      }
    }
    pc.addEventListener('iceconnectionstatechange', mainIceListener);
    resolve();
  }).then(function () {
    // car controller
    var dc = pc.createDataChannel('car');
    dc.onerror = console.log
    dc.onclose = console.log
    dc.onopen = function () {
      console.log('data channel opened');
      window.onkeydown = throttle(function (e) {
        dc.send(e.key);
      }, 200);
    }
  }).then(function () {
    pc.addTransceiver('video', { direction: 'recvonly' });
    pc.addTransceiver('audio', { direction: 'recvonly' });
    return pc.createOffer()
  }).then(function (offer) {
    return pc.setLocalDescription(offer);
  }).then(function () {
    // wait for ICE gathering to complete
    return new Promise(function (resolve) {
      if (pc.iceGatheringState === 'complete') {
        resolve();
      } else {
        function checkState() {
          if (pc.iceGatheringState === 'complete') {
            pc.removeEventListener('icegatheringstatechange', checkState);
            resolve();
          }
        }
        pc.addEventListener('icegatheringstatechange', checkState);
      }
    });
  }).then(function () {
    var offer = pc.localDescription;
    console.log('Offer SDP');
    console.log(offer.sdp);
    return fetch('/offer', {
      body: JSON.stringify({
        sdp: offer.sdp,
        type: offer.type,
      }),
      headers: {
        'Content-Type': 'application/json'
      },
      method: 'POST'
    });
  }).then(function (response) {
    return response.json();
  }).then(function (answer) {
    console.log('Answer SDP');
    console.log(answer.sdp);
    return pc.setRemoteDescription(answer);
  }).catch(function (e) {
    console.error(e);
  });
  return pc;
}

// Use on firefox
function getCurrentFrame() {
  var canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  var canvasContext = canvas.getContext("2d");
  canvasContext.drawImage(video, 0, 0);
  return canvas.toDataURL('image/png');
}

function isVideoFrozen(pc) {
  var previousFrame;
  var ignoreFirst = true;
  vfdIntervalId = setInterval(function () {
    if (peerConnectionGood(pc) && video.currentTime > 0 && getCurrentFrame() === previousFrame) {
      if (ignoreFirst) {
        ignoreFirst = false;
        return
      }
      console.warn("Video freeze detected using frames!!!");
      reconnect();
    } else {
      previousFrame = getCurrentFrame();
    }
  }, 3000);
}

// Use on Chrome
function checkVideoFreeze(pc) {
  var previousPlaybackTime;
  vfdIntervalId = setInterval(function () {
    if (peerConnectionGood(pc) && previousPlaybackTime === video.currentTime && video.currentTime !== 0) {
      console.warn("Video freeze detected!!!");
      reconnect();
    } else {
      previousPlaybackTime = video.currentTime;
    }
  }, 3000);
}

function startVideoFreezeDetection(pc) {
  stopVideoFreezeDetection();
  if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
    isVideoFrozen(pc);
  } else {
    checkVideoFreeze(pc);
  }
}

function stopVideoFreezeDetection() {
  if (vfdIntervalId !== null) {
    console.log('Stopping Current Video Freeze Detector');
    clearInterval(vfdIntervalId);
  }
}

function cleanup() {
  if (backupPeerConnection !== null) {
    console.log('Cleaning Up...')
    var tmp = primaryPeerConnection;
    primaryPeerConnection = backupPeerConnection;
    backupPeerConnection = tmp;
    backupPeerConnection.close();
    backupPeerConnection = null;
    var thisInterval = setInterval(function () {
      if (peerConnectionGood(primaryPeerConnection) && backupPeerConnection === null) {
        showContainer('video');
        clearInterval(thisInterval);
      }
    }, 100);
  }
}

function reconnect() {
  console.log('Reconnecting');
  backupPeerConnection = createNewPeerConnection();
}

var isSafari = !!navigator.userAgent.match(/Version\/[\d\.]+.*Safari/);
var iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
var safariOnIos = isSafari && iOS;
if (window.navigator.userAgent.indexOf("Edge") > -1 || safariOnIos) {
  //state 3 means the client is a Microsoft Edge or Safari on iOS
  state = 3;
  alert('not supported')
} else {
  primaryPeerConnection = createNewPeerConnection();
}

function throttle(fn, threshhold) {

  // 记录上次执行的时间
  var last

  // 定时器
  var timer

  // 默认间隔为 250ms
  threshhold || (threshhold = 250)

  // 返回的函数，每过 threshhold 毫秒就执行一次 fn 函数
  return function () {

    // 保存函数调用时的上下文和参数，传递给 fn
    var context = this
    var args = arguments

    var now = +new Date()

    // 如果距离上次执行 fn 函数的时间小于 threshhold，那么就放弃
    // 执行 fn，并重新计时
    if (last && now < last + threshhold) {
      clearTimeout(timer)

      // 保证在当前时间区间结束后，再执行一次 fn
      timer = setTimeout(function () {
        last = now
        fn.apply(context, args)
      }, threshhold)

      // 在时间区间的最开始和到达指定间隔的时候执行一次 fn
    } else {
      last = now
      fn.apply(context, args)
    }
  }
}

document.getElementById('audio-btn').onclick = function () {
  this.remove();
  document.getElementById('video').muted = false
}