rtmp-client
==

## Description
RTMP client for Python. This project was created for deepen my understanding to RTMP protocol.

## Usage
publish to remote client
```
$ echo "test message" | python3 bin/rtmp-client publish 
```

subscribe from publisher
```
$ python3 bin/rtmp-client play
```