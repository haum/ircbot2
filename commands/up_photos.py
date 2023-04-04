#!/usr/bin/env python3

from threading import Thread
from core.permissions import priviledged

def help(bot, msg):
    bot.msg('!up_photos: Update photos website')

worker = None

@priviledged
def command(bot, msg, is_privileged):
    global worker
    if worker and worker.is_alive():
        bot.msg('est en train de reconstruire le site de photos.', True)
    else:
        worker = Thread(target=update_thread_run, args=(bot,))
        worker.start()

def update_thread_run(bot):
    bot.msg('Mise à jour du site de photos...')

    import os
    import json
    import piexif
    import html
    from datetime import datetime
    from PIL import Image

    photosdir = '/www/photos.haum.org/albums'
    thumbsdir = "/www/photos.haum.org/thumbs"
    smalldir = "/www/photos.haum.org/small"
    globalindex = "/www/photos.haum.org/index.html"
    metadatafile = '_data.json'
    photoext = ('.jpg', '.jpeg', '.png')

    def getMetadata(album):
        ret = {
            'title': album,
            'desc': '',
            'thumb': '',
            'date': '',
            'album': album,
        }
        try:
            with open(photosdir + '/' + album + '/' + metadatafile) as jsonfile:
                data = json.load(jsonfile)
                for k in data:
                    if k in ret:
                        ret[k] = data[k]
                if 'date' in data:
                    ret['date'] = datetime.strptime(data['date'], '%Y-%m-%d') # b'2016-08-12'
        except FileNotFoundError:
            print('No _data.json for folder ' + album)

        if not ret['desc']:
            ret['desc'] = ret['title']
        if not ret['thumb']:
            ret['thumb'] = first_photo_name(album)
        if not ret['date']:
            ret['date'] = find_date_album(album)

        return ret

    def find_date_photo(album, photo):
        if os.path.splitext(photo)[1].lower() in ('.jpg', '.jpeg'):
            exif_dict = piexif.load(photosdir + '/' + album + '/' + photo)['Exif']
            if 36867 in exif_dict:
                date = exif_dict[36867].decode('ascii')
                if date != '0000:00:00 00:00:00':
                    return datetime.strptime(date, '%Y:%m:%d %H:%M:%S') # b'2016:08:12 19:57:39'
        return datetime(2012, 1, 1)

    def find_date_album(album):
        maxdate = None
        for photo in os.listdir(photosdir + '/' + album):
            date = find_date_photo(album, photo)
            if not maxdate:
                maxdate = date
            elif date:
                maxdate = max(maxdate, date)
        if not maxdate:
            maxdate = datetime(2012, 1, 1)
        return maxdate

    def first_photo_name(album):
        for photo in os.listdir(photosdir + '/' + album):
            if os.path.splitext(photo)[1].lower() in photoext:
                return photo

    def create_thumbnail(album, photo):
        recreate = True
        try:
            if os.path.getmtime(photosdir+'/'+album+'/'+photo) <= os.path.getmtime(thumbsdir+'/'+album+'/'+photo):
                recreate = False
        except FileNotFoundError:
            pass
        if os.path.splitext(photo)[1].lower() in photoext and recreate:
            os.makedirs(thumbsdir + '/' + album, exist_ok=True)
            print(photosdir+'/'+album+'/'+photo)
            im = Image.open(photosdir+'/'+album+'/'+photo)
            im.thumbnail((200,200), Image.ANTIALIAS)
            im.save(thumbsdir+'/'+album+'/'+photo)
            print("Thumbnail " + album + '/' + photo)

    def create_smallimg(album, photo):
        recreate = True
        try:
            if os.path.getmtime(photosdir+'/'+album+'/'+photo) <= os.path.getmtime(smalldir+'/'+album+'/'+photo):
                recreate = False
        except FileNotFoundError:
            pass
        if os.path.splitext(photo)[1].lower() in photoext and recreate:
            os.makedirs(smalldir + '/' + album, exist_ok=True)
            im = Image.open(photosdir+'/'+album+'/'+photo)
            im.thumbnail((640,640), Image.ANTIALIAS)
            im.save(smalldir+'/'+album+'/'+photo)
            print("Make small image " + album + '/' + photo)

    def create_album_page(album):
        photos = []
        album_metadata = getMetadata(album)
        for photo in os.listdir(photosdir + '/' + album):
            if os.path.splitext(photo)[1].lower() in photoext:
                date = find_date_photo(album, photo)
                photos.append({'photo': photo, 'date': date})

        f = open(photosdir + '/' + album + "/index.html", "w")
        f.write("""<!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    """)
        f.write('		<meta property="og:title" content="' + album_metadata['title'] + '" />\n')
        f.write('		<meta property="og:type" content="website" />\n')
        f.write('		<meta property="og:site_name" content="Photos|HAUM.org" />\n')
        f.write('		<meta property="og:url" content="https://photos.haum.org/albums/' + album + '/" />\n')
        f.write('		<meta property="og:image" content="https://photos.haum.org/thumbs/' + album + '/' + album_metadata['thumb'] + '" />\n')
        f.write('		<meta property="og:description" content="' + album_metadata['desc'] + '" />\n')
        f.write('		<title>Albums: ' + album_metadata['title'] + '</title>\n')
        f.write("""
            <script type="text/javascript" src="../../_unitegallery/js/jquery-11.0.min.js"></script>
            <script type="text/javascript" src="../../_unitegallery/js/unitegallery.min.js"></script>
            <link rel="stylesheet" href="../../_unitegallery/css/unite-gallery.css" type="text/css" />
            <script type="text/javascript" src="../../_unitegallery/themes/tiles/ug-theme-tiles.js"></script>
            <style>
                body { background: #333; color: #fff; }
                h1 { text-align: center; color: #eee; }
                            a { color: #aaa; }
                            #gallery { margin-top: 10px; }
            </style>
        </head>

        <body>
    """)
        f.write('		<h1>' + album_metadata['title'] + '</h1>\n')
        f.write('           <a href="../..">&lt; Retour aux albums</a>\n');
        if album_metadata['desc']:
            f.write('		<p>' + album_metadata['desc'] + '</p>\n')
        f.write('		<div id="gallery">\n')
        for photo in sorted(photos, key=lambda x: x['date'], reverse=True):
            create_thumbnail(album, photo['photo'])
            create_smallimg(album, photo['photo'])
            f.write('           <img src="../../thumbs/' + album + '/' + photo['photo'] + '" data-image="' + photo['photo'] + '" alt="" data-description="" />\n')
        f.write("""		</div>
            <script type="text/javascript">
                jQuery(document).ready(function(){
                    jQuery("#gallery").unitegallery();
                });
            </script>
        </body>
    </html>
    """) 


    def create_index():
        albums = []
        for album in os.listdir(photosdir):
            if os.path.isdir(photosdir + '/' + album):
                albums.append(getMetadata(album))

        f = open(globalindex, "w")
        f.write("""<!DOCTYPE html>
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Albums</title>
            <style>
                body { background: #333; color: #fff; }
                h1 { text-align: center; color: #eee; }
                a { color: #aaa; text-decoration: none; }
                li {
                  float: left;
                  height: 210px;
                  border: solid 1px black;
                  background: #222;
                  padding: 10px;
                  margin: 10px;
                  text-align: center;
                  list-style-type: none;
                }
                li div {
                  width: 210px;
                  height: 210px;
                  margin: 0;
                  padding: 0;
                  display: table-cell;
                  vertical-align: middle;
                  text-align: center
                }
            </style>
        </head>
        <body>
            <h1>Albums</h1>
            <ul>
    """)
        for album in sorted(albums, key=lambda x: x['date'], reverse=True):
            print(album)
            create_album_page(album['album'])
            f.write('           <li><a href="' + photosdir + '/' + album['album'] + '/"><div><img src="' + thumbsdir + '/' + album['album'] + '/' + album['thumb'] + '" /></div><div>' + html.escape(album['title']) + '</div></a></li>\n')
        f.write("""        </ul>
        </body>
    </html>
    """) 

    create_index()

    # End
    bot.msg('Site de photos à jour.')
