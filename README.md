## Readme

This project aims to create a media center site for home use.

* Provide universal access to private media stored on your big storage device

* Provide Movie Rating System that grant control over different rating of videos for different people

* Smart information collection with lightweight spiders

* Backup service that upload local important files to 3rd party cloud service

## Kick Start

1. ./manage.py migrate
   Create database files

2. Create users:
   ./manage.py createsuperuser
   
3. ./collect_video [your dir containing mp4 videos] rating=(G|PG|PG13|NC17|P)
   Your files will be retrieved recursively, all .mp4 files will be collected to database.
   Covers/thumbnails/flips(fake animated preview pictures) will be generated during this process,
   and they will be put to static/cover, static/thumb, static/flip respectively
   
2. ./manage.py runserver ip_addr:port_number
   Now your home site is on the go!
   
4. Adding other users   
   Admin url is /admin . If you need to manage users you need to visit it manually - this entry is not provided on index page.

## Features

* HTML5 based main page that is flexible on PC/mobile devices

* Lightweight keyword search based on keywords collected from file path 

* HTML 5 player that provides  universal access on PC/mobile devices

* Build video database from specified position, generate thumbnails for each video and convert them when necessary

* Movie Rating System that is similar to the American version, allowing rating control for home with kids

* Basic https support

## Prequisites

* Django 1.10   
* Python 2.7  
* FFmpeg with png/h264 codec
* openssl


## Preview

### Index Page
![index page](http://wx1.sinaimg.cn/large/83e56decgy1fidix9ektmj20x70di7ff.jpg)

### Player Page
![player_page](http://wx4.sinaimg.cn/large/83e56decgy1fidix5wskuj20xk0qk4ko.jpg)

### Manage Page

![manage_1](http://wx1.sinaimg.cn/large/83e56decgy1fidix8fy76j20zy0n979j.jpg)
![manage_2](http://wx2.sinaimg.cn/large/83e56decgy1fidixa4v9qj215y0fswja.jpg)
![manage_3](http://wx3.sinaimg.cn/large/83e56decgy1fidix7nicdj20xm0b0wfo.jpg)

### Movie Rating System

![movie_rating](http://wx2.sinaimg.cn/large/83e56decgy1fidix6tp5ej20zj0n1n2v.jpg)


## Appendix: Movie Rating System
    
The website provides a Movie Rating System that is similar to the American one, except that it added a "P" rating, which means the video is totally private and you don't wish it be watched by others.
Rating "P" was added simply to avoid misunderstanding.
Videos are provided with a rating when importing with collect_video, and it's "P" by default, which is the highest level.

Anonymous users are granted with the lowest "G" level. They can visit the site without logging in - so be careful importing videos with "G"

 
The rating levels are: 

* G: For general audiences
* PG: Parental guidance
* PG13: Parents Strongly Cautioned
* R: Restricted
* NC17: NO ONE AND UNDER 17 ADMITTED
* Private: Videos for private access
