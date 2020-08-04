# scan-for-webcams :camera:

Automatically scan for publically accessible webcams around the internet

[中文文档](/zh/README.md)
## Table of contents

- [Usage](#Usage)
- [Installation](#Installation)
- [Demo](#Demo)

## Usage

* ` python MJPG.py ` : for public [MJPG streamers](https://github.com/jacksonliam/mjpg-streamer) around the internet

* ` python webcamXP.py ` : for public [webcamXP streamers](http://www.webcamxp.com/) around the internet

The program will output a list of links with the format of `ip_address:port`

If your terminal supports links, click the link and open it in your browser, otherwise, copy the link and open it in your browser.

## Installation

1. clone&cd into the repo:

   ` git clone https://github.com/JettChenT/scan-for-webcams;cd scan-for-webcams `

2. install requirements:

   `pip install -r requirements.txt`

3. set up shodan:

   1. go to [shodan.io](https://shodan.io), register/log in and grab your API key

   2. Set environ `SHODAN_API_KEY` as your `API key`:

      ` export "SHODAN_API_KEY"="<your api key>" `
4. set up clarifai:
   1. go to [clarifai.com](https://clarifai.com), register/log in, create an application and grab your API key
   2. set environ `CLARIFAI_API_KEY` as your `API key`
        
        ` export "CLARIFAI_API_KEY"="<your api key>" `

And then you can run the program!

## Demo

[![asciicast](https://asciinema.org/a/349819.svg)](https://asciinema.org/a/349819)
