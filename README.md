# scan-for-webcams :camera:

![scan-for-webcamBanner](./.github/scan-for-webcamBanner.png)

![PyPI - License](https://img.shields.io/pypi/l/scan-for-webcams?style=flat-square)
[![Discord server invite](https://discordapp.com/api/guilds/974876463797006356/embed.png)](https://discord.gg/JCepvsHNqW)

[中文文档](/zh/README.md)

## Note
I switched to a new method of [installing](#Installation) this program 
for a better developer experience and better modifiability.

As a result, the PYPI package `scan-for-webcams` is not maintained anymore, and 
should be considered deprecated.

btw: we have a discord channel ! [join](https://discord.gg/JCepvsHNqW)

## Table of contents

- [scan-for-webcams :camera:](#scan-for-webcams-camera)
  - [Note](#note)
  - [Table of contents](#table-of-contents)
  - [Usage](#usage)
  - [Installation](#installation)
  - [Places365: On device footage classification](#places365-on-device-footage-classification)
  - [Graphical User Interface](#graphical-user-interface)
  - [Demo](#demo)

## Usage

* `python sfw search MJPG` : for public [MJPG streamers](https://github.com/jacksonliam/mjpg-streamer)

* `python sfw search webcamXP` : for public [webcamXP streamers](http://www.webcamxp.com/)

* `python sfw search yawCam`: for public [yawCam steamers](https://www.yawcam.com/)

* `python sfw search hipcam`: for public hipcam streamers

* `python sfw search rtsp`: **DANGER** searches for rtsp servers on shodan, and performs enumeration on them to try and find streams


* `python sfw play {url}`: plays the camera stream
  * for `rtsp://` streams, sfw will play it in a GUI viewer (see `sfw/rtsp.py`)
  * for all other streams, sfw will open it in the default browser.

* `python sfw search ... --gui`: displays the scanned cameras in a grid visually.

* `python sfw search --help`: for more options and help

The program will output a list of links with the format of `ip_address:port`, and descriptions of the image beneath it.

If your terminal supports links, click the link and open it in your browser, otherwise, copy the link and open it in your browser.

## Installation
1. Clone this repository: `git clone https://github.com/JettChenT/scan-for-webcams`

2. install requirements.txt: `pip install -r requirements.txt`

3. install tkinter: `sudo apt-get install python3-tk`

4. set up shodan:
   go to [shodan.io](https://shodan.io), register/log in and grab your API key

5. set up clarifai:
   go to [clarifai.com](https://clarifai.com), register/log in, create an application and grab your API key.
   Alternatively, use the local [places365](#places365-on-device-footage-classification) model.

6. setup geoip:
   go to [geo.ipify.org](https://geo.ipify.org), register/log in and grab your API key
   
7. Add API keys:
   1. run `python sfw setup`
   2. enter your shodan, clarifai and geoip API keys

And then you can [run](#Usage) the program!

## Places365: On device footage classification
It is now possible to run [the Places365 model](https://github.com/CSAILVision/places365),
a model fined tuned for real world locations,
to get information about webcam footage.

To use this model, you need to install the following packages:
```bash
pip install -r requirements-places.txt
```

Then, you can run the program with the `--places` flag:
```
python sfw search MJPG --tag=False --places
```

The model will take some time to download, and will be cached for future use.

## Graphical User Interface

To get a display of the live streams of all the scanned webcams, simply append the `--gui` option to your command.

## Demo

[![asciicast](https://asciinema.org/a/494164.svg)](https://asciinema.org/a/494164)
