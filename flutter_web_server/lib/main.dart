import 'package:flutter/material.dart';
import 'package:flutter_web_server/src/p2p_video.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Material App',
      home: P2PVideo(),
    );
  }
}
