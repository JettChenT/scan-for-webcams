# scan-for-webcams :camera:

![scan-for-webcamBanner](./.github/scan-for-webcamBanner.png)

[中文文档](/zh/README.md)

## Table of contents

- [Usage](#Usage)
- [Installation](#Installation)
- [Demo](#Demo)

## Usage

* ` python main.py search MJPG` : for public [MJPG streamers](https://github.com/jacksonliam/mjpg-streamer)

* ` python main.py search webcamXP` : for public [webcamXP streamers](http://www.webcamxp.com/)

* `python main.py search yawCam`: for public [yawCam steamers](https://www.yawcam.com/)

* ` python main.py search --help`: for more options and help

The program will output a list of links with the format of `ip_address:port`, and descriptions of the image beneath it.

If your terminal supports links, click the link and open it in your browser, otherwise, copy the link and open it in your browser.

## Installation

1. clone&cd into the repo:

   ` git clone https://github.com/JettChenT/scan-for-webcams;cd scan-for-webcams `

2. install requirements:

   `pip install -r requirements.txt`

3. set up shodan:

   1. go to [shodan.io](https://shodan.io), register/log in and grab your API key

   2. Edit .env, set SHODAN_API_KEY to your api key:

      ` SHODAN_API_KEY=YOUR_API_KEY `
4. set up clarifai:
   1. go to [clarifai.com](https://clarifai.com), register/log in, create an application and grab your API key
   2. Edit .env, set CLARIFAI_API_KEY to your api key:
     
       ` CLARIFAI_API_KEY=YOUR_API_KEY `

And then you can run the program!

## Demo

[![asciicast](https://asciinema.org/a/366018.svg)](https://asciinema.org/a/366018)
