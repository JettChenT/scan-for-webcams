# scan-for-webcams :camera:

自动探测可公开访问的网络摄像头

[中文文档](/zh/README.md)

## 目录

- [使用方法](#Usage)
- [下载安装](#Installation)
- [演示](#Demo)

## 使用方法

- `python MJPG.py` : 用来探测公开的 [MJPG 播放器](https://github.com/jacksonliam/mjpg-streamer)

- `python webcamXP.py` : 用来检测公开的 [webcamXP 播放器](http://www.webcamxp.com/)

程序会输出一列地址，格式如： `ip_address:port`

如果您的终端支持链接，请单击该链接并在浏览器中将其打开，否则，请复制该链接并在浏览器中将其打开。

## 下载装

1. clone&cd 进这个repo:

    `git clone https://github.com/JettChenT/scan-for-webcams;cd scan-for-webcams`

2. 安装要求：

    `pip install -r requirements.txt`

3. 设立 shodan 服务：

    1. 前往 [shodan.io](https://shodan.io), 注册并登陆进去，然后获得你的 API 密钥

    2. 设置环境变量  `SHODAN_API_KEY` 为你的 `API 密钥`:

        `export "SHODAN_API_KEY"="<你的API密钥>"`

然后就可以运行程序了！

## 演示

[](https://asciinema.org/a/349819)![asciicast](https://asciinema.org/a/349819.svg)
