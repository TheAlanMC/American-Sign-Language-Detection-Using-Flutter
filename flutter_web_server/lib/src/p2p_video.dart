import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http.dart' as http;

//const String baseUrl = 'http://192.168.0.29:8080';
const String baseUrl = 'http://192.168.43.24:8080';
// const String baseUrl = 'http://172.20.10.2:8080';

class P2PVideo extends StatefulWidget {
  const P2PVideo({Key? key}) : super(key: key);

  @override
  P2PVideoState createState() => P2PVideoState();
}

class P2PVideoState extends State<P2PVideo> {
  RTCPeerConnection? _peerConnection;
  final _localRenderer = RTCVideoRenderer();
  MediaStream? _localStream;

  String transformType = 'Principal';
  RTCDataChannelInit? _dataChannelDict;
  RTCDataChannel? _dataChannel;

  bool _inCalling = false;
  bool _loading = false;
  bool _isFrontal = false;

  void _onTrack(RTCTrackEvent event) {
    // print("TRACK EVENT: ${event.streams.map((e) => e.id)}, ${event.track.id}");
    if (event.track.kind == "video") {
      // print("HERE");
      _localRenderer.srcObject = event.streams[0];
    }
  }

  void _onDataChannelState(RTCDataChannelState? state) {
    switch (state) {
      case RTCDataChannelState.RTCDataChannelClosed:
        // print("Camera Closed!!!!!!!");
        break;
      case RTCDataChannelState.RTCDataChannelOpen:
        // print("Camera Opened!!!!!!!");
        break;
      default:
      // print("Data Channel State: $state");
    }
  }

  Future<bool> _waitForGatheringComplete(_) async {
    // print("WAITING FOR GATHERING COMPLETE");
    if (_peerConnection!.iceGatheringState == RTCIceGatheringState.RTCIceGatheringStateComplete) {
      return true;
    } else {
      await Future.delayed(const Duration(seconds: 1));
      return await _waitForGatheringComplete(_);
    }
  }

  Future<void> _toggleCamera() async {
    _isFrontal = !_isFrontal;
    if (_localStream == null) throw Exception('Stream is not initialized');

    final videoTrack = _localStream!.getVideoTracks().firstWhere((track) => track.kind == 'video');
    await Helper.switchCamera(videoTrack);
  }

  Future<void> _negotiateRemoteConnection() async {
    return _peerConnection!
        .createOffer()
        .then((offer) {
          return _peerConnection!.setLocalDescription(offer);
        })
        .then(_waitForGatheringComplete)
        .then((_) async {
          var des = await _peerConnection!.getLocalDescription();
          var headers = {
            'Content-Type': 'application/json',
          };
          var request = http.Request(
            'POST',
            Uri.parse('$baseUrl/offer'),
          );
          request.body = json.encode(
            {
              "sdp": des!.sdp,
              "type": des.type,
              "video_transform": transformType,
            },
          );
          request.headers.addAll(headers);

          http.StreamedResponse response = await request.send();

          String data = "";
          // print(response);
          if (response.statusCode == 200) {
            data = await response.stream.bytesToString();
            var dataMap = json.decode(data);
            // print(dataMap);
            await _peerConnection!.setRemoteDescription(
              RTCSessionDescription(
                dataMap["sdp"],
                dataMap["type"],
              ),
            );
          } else {
            // print(response.reasonPhrase);
          }
        });
  }

  Future<void> _makeCall({bool initial = true, bool toggle = false}) async {
    setState(() {
      _loading = true;
    });

    if (_isFrontal) await _toggleCamera();

    var configuration = <String, dynamic>{
      'sdpSemantics': 'unified-plan',
    };

    // Crea el peer connection
    if (_peerConnection != null) return;
    _peerConnection = await createPeerConnection(
      configuration,
    );

    _peerConnection!.onTrack = _onTrack;

    //* Crea el canal de datos
    _dataChannelDict = RTCDataChannelInit();
    _dataChannelDict!.ordered = true;
    _dataChannel = await _peerConnection!.createDataChannel(
      "chat",
      _dataChannelDict!,
    );
    _dataChannel!.onDataChannelState = _onDataChannelState;

    final mediaConstraints = <String, dynamic>{
      'audio': false,
      'video': {
        'width': '480',
        'height': '720',
        'facingMode': 'environment',
        'optional': [],
      }
    };

    try {
      var stream = await navigator.mediaDevices.getUserMedia(mediaConstraints);
      _localStream = stream;
      stream.getTracks().forEach((element) {
        _peerConnection!.addTrack(element, stream);
      });
      // print("Negotiating");
      await _negotiateRemoteConnection();
      if (transformType == 'Frontal') {
        await _toggleCamera();
      }
    } catch (e) {
      // print(e.toString());
    }
    if (!mounted) return;
    setState(() {
      _inCalling = true;
      _loading = false;
    });
  }

  Future<void> _stopCall() async {
    try {
      await _dataChannel?.close();
      await _peerConnection?.close();
      _peerConnection = null;
      _localRenderer.srcObject = null;
    } catch (e) {
      // print(e.toString());
    }
    setState(() {
      _inCalling = false;
    });
  }

  Future<void> initLocalRenderers() async {
    await _localRenderer.initialize();
  }

  @override
  void initState() {
    super.initState();

    initLocalRenderers();
  }

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        backgroundColor: _inCalling ? Colors.black : Colors.indigo.shade100,
        body: OrientationBuilder(
          builder: (context, orientation) {
            return Stack(
              children: [
                if (!_inCalling)
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Card(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20),
                            ),
                            elevation: 10,
                            child: const Image(image: AssetImage('assets/asl.png'), height: 200),
                          ),
                        ),
                        const SizedBox(height: 50),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Text('Cámara:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                            const SizedBox(width: 10),
                            DropdownButton(
                              value: transformType,
                              onChanged: (value) {
                                setState(() {
                                  transformType = value.toString();
                                });
                              },
                              items: ['Principal', 'Frontal']
                                  .map(
                                    (e) => DropdownMenuItem(
                                      value: e,
                                      child: Text(
                                        e,
                                      ),
                                    ),
                                  )
                                  .toList(),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                if (_inCalling)
                  SizedBox(
                    width: MediaQuery.of(context).size.width,
                    height: MediaQuery.of(context).size.height,
                    child: Stack(
                      children: [
                        Positioned.fill(
                          child: Container(
                            color: Colors.black,
                            child: _loading
                                ? const Center(
                                    child: CircularProgressIndicator(
                                      strokeWidth: 4,
                                    ),
                                  )
                                : Container(),
                          ),
                        ),
                        Positioned.fill(
                          child: RTCVideoView(
                            _localRenderer,
                          ),
                        ),
                      ],
                    ),
                  ),
                Positioned(
                  bottom: 10,
                  child: SizedBox(
                    width: MediaQuery.of(context).size.width,
                    child: Center(
                      child: InkWell(
                        onTap: _loading
                            ? () {}
                            : _inCalling
                                ? _stopCall
                                : _makeCall,
                        child: Container(
                          decoration: BoxDecoration(
                            color: _loading
                                ? Colors.amber
                                : _inCalling
                                    ? Colors.red
                                    : Theme.of(context).primaryColor,
                            borderRadius: BorderRadius.circular(15),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            child: _loading
                                ? const Padding(
                                    padding: EdgeInsets.all(8.0),
                                    child: CircularProgressIndicator(),
                                  )
                                : Text(
                                    _inCalling ? "STOP" : "START",
                                    style: const TextStyle(
                                      fontSize: 24,
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
