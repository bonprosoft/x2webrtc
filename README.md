# x2webrtc
[![PyPI](https://img.shields.io/pypi/v/x2webrtc.svg)](https://pypi.org/project/x2webrtc/)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/x2webrtc.svg)](https://pypi.org/project/x2webrtc/)
[![GitHub license](https://img.shields.io/github/license/bonprosoft/x2webrtc.svg)](https://github.com/bonprosoft/x2webrtc)

x2webrtc is a command-line tool for forwarding an X window as a media track through WebRTC.  It is a simple tool; it just grabs screenshots for the window with Xlib and send them via a WebRTC stream, but it can realize the following features:
You can send an X window through the NAT.
A media stream is transported using a secure method. (compared to the standard VNC)
You can easily install it by pip.
You don't necessarily have admin access to the system.

## Install

Note that Python 3.6+ and X Window System are required to use the tool.

```sh
pip install x2webrtc
```

The tool requires `aiortc` to work with WebRTC.
Please refer to [the install instruction](https://github.com/aiortc/aiortc#linux) of `aiortc` if you failed to install it automatically.

## Quickstart

**NOTE**:
Currently, hand signaling is required to start a WebRTC session.
I am planning to implement a plug-in system so that a user can customize its signaling method.

1. Start x2webrtc.

    ```sh
    x2webrtc forward
    ```

    If `DISPLAY` environment is not set to your environment, pass `--display` argument to specify an X server.

    ```
    x2webrtc forward --display :0
    ```

2. (tentative) Copy a WebRTC offer.
You will see the following message on your terminal:

    ```
    -- Please send this message to the remote party --
    {"sdp": "..." , "type": "offer"}
    ```

    Please copy the offer json.

3. (tentative) Open the web client and click `Connect` button.
4. (tentative) Paste the offer json into `Input Offer` text-area (A) and click `Create Answer` button (B). Then you will get an answer json (C). Copy the json again.
![](https://raw.githubusercontent.com/bonprosoft/x2webrtc/master/imgs/quick_start_web_client.png)
5. (tentative) Go back to your terminal. Paste the answer json into the terminal, then press Enter.
6. Now you will see your screen in the web client.

## Usage

```
usage: x2webrtc [-h] [-v] COMMANDS ...

Commands:
    forward       forward X Window
    info          show window information of the X server

optional arguments:
  -h, --help      show this help message and exit
  -v, --verbose   verbose; can be used up to 3 times to increase verbosity
```

### x2webrtc forward

Forward a specified X window.

```
usage: x2webrtc forward [-h] [--display DISPLAY]

optional arguments:
  -h, --help         show this help message and exit
  --display DISPLAY  display_name of the X server to connect to (e.g., hostname:1, :1.)
```

### x2webrtc info

Show information on a specified X server.

```
usage: x2webrtc info [-h] [--display DISPLAY] [--props]

optional arguments:
  -h, --help         show this help message and exit
  --display DISPLAY  display_name of the X server to connect to (e.g., hostname:1, :1.)
  --props            show all properties of each window
```

## FAQ

### Failed to install PyAV
`PyAV` uses `AV_CODEC_CAP_HARDWARE` macro in its source code, but it seems to be available in `libavcodec >= 58.0`. Check the version of libavcodec and try again.
