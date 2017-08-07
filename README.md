## Readme

This project aims to create a media center site for home use.

* Provide universal access to private media stored on your big storage device

* Provide live broadcast that connect monitor/smartphones together

* Smart information collection with lightweight spiders

* Backup service that upload local important files to 3rd party cloud service

## Kick Start

1. ./collect_video [your dir containing mp4 videos]
   Your files will be retrieved recursively, all .mp4 files will be collected to database.
   Covers/thumbnails/flips(fake animated preview pictures) will be generated during this process,
   and they will be put to static/cover, static/thumb, static/flip respectively
2. ./manage.py runserver ip_addr:port_number
   Now your home site is on the go!

## Implemented Features

* HTML5 based main page that is flexible on PC/mobile devices

* Lightweight keyword search based on keywords collected from file path 

* HTML 5 player that provides  universal access on PC/mobile devices

* Build video database from specified position, generate thumbnails for each video and convert them when necessary

## TODO List

#### HTML5 Video Player

* [x] Better player appearance

* [ ] Add tags to the video

* [x] Like/Disklike count
 
* [ ] Play count

* [ ] Movie rating system + Account system

* [ ] Delete video with supervisor account

* [ ] Recommend videos beside the player

* [ ] Convert button

#### Video Collection

* Provide web access to video collection and management

* Background task to convert videos when CPU is idle
 

#### Live broadcast

* Implement iOS client for HLS streaming

* Implement backend supporting HLS delivery

* Further research for broadcast using Flash

## Prequisites

* Django 1.10   
* Python 2.7  
* FFmpeg with png/h264 codec
* openssl


## Default super user

username: ethan   
password: ethanlovewinston

## Preview

![preview-1](http://wx3.sinaimg.cn/mw690/83e56decgy1fdmbjhl8dqj20l00ltk4z.jpg)
![preview-2](http://wx2.sinaimg.cn/large/83e56decgy1fdmbjjbtutj20wp0gydtk.jpg)


