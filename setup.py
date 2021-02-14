from setuptools import setup, find_packages
import sys
import os

version = sys.version_info[:2]
if version<(3,6):
    print("scan-for-webcams require python version >= 3.6")
    print("{}.{} detected".format(*version))
    sys.exit(-1)
VERSION = "1.2.4"
reqs = ['shodan','requests','rich','pillow','clarifai','halo','fire','python-dotenv']

with open("README.md", "r") as fh: 
    long_description = fh.read() 

setup(
    name="scan-for-webcams",
    version=VERSION,
    author="Jett Chen",
    author_email="contact@jettchen.me",
    url="https://github.com/JettChenT/scan-for-webcams",
    license="MIT",
    packages=find_packages(),
    install_requires=reqs,
    long_description=long_description, 
    long_description_content_type="text/markdown", 
    package_data={
        'scanforwebcams':['*.json'],
    },
    entry_points= {'console_scripts':[
          'sfw=scanforwebcams.universal:Main']
        }
)
