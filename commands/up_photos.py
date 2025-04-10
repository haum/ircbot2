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

    wwwpath = '/www/photos.haum.org/'
    photosdirname = 'albums'
    photosdir = wwwpath + photosdirname
    thumbsdirname = "thumbs"
    thumbsdir = wwwpath + thumbsdirname
    smalldirname = "small"
    smalldir = wwwpath + smalldirname
    globalindex = wwwpath + 'index.html'
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
            im.thumbnail((200,200), Image.LANCZOS)
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
            im.thumbnail((640,640), Image.LANCZOS)
            im.save(smalldir+'/'+album+'/'+photo)
            print("Make small image " + album + '/' + photo)

    def create_album_page(album):
        photos = []
        album_metadata = getMetadata(album)
        for photo in os.listdir(photosdir + '/' + album):
            if os.path.splitext(photo)[1].lower() in photoext:
                date = find_date_photo(album, photo)
                p = {'photo': photo, 'date': date, 'preset': 'mono', 'video': False}
                parts = photo.replace('_', '.').replace('-', '.').split('.')
                if 'sbs' in parts:
                    p['preset'] = 'sbs'
                if 'mp4' in parts:
                    p['video'] = True
                photos.append(p)

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
            <style>
                body { background: #333; color: #fff; }
                h1 { text-align: center; color: #eee; }
                            a { color: #aaa; }
			.thumbnails {
				margin-top: 10px;
				display: flex;
				flex-wrap: wrap;
				justify-content: space-around;
			}
			.thumbnails::after {
				content: "";
				flex: auto;
			}
			img {
				border: 4px solid black;
				align-self: center;
				margin: 5px;
			}
			img.active {
				border-color: #0af;
			}
            </style>
        </head>

        <body>
    """)
        f.write('		<h1>' + album_metadata['title'] + '</h1>\n')
        f.write('           <a href="../..">&lt; Retour aux albums</a>\n');
        if album_metadata['desc']:
            f.write('		<p>' + album_metadata['desc'] + '</p>\n')
        f.write("""		<script type="text/javascript">
			var last_active = 0;
			var imgs = null;
			window.addEventListener('message', function(e) {
				if (!imgs)
					imgs = document.getElementsByClassName('thumbnails')[0].getElementsByTagName('img');
				if (e.origin == 'https://stereopix.net') {
					if (e.data.type == 'viewerReady') {
						var json = { "media": [] };
						for (var i = 0; i < imgs.length; i++) {
							if ('video' in imgs[i].dataset)
								json.media.push({ "url": (new URL(imgs[i].dataset.video, document.location.href)).href, "preset": imgs[i].dataset.preset, "video": true });
							else
								json.media.push({ "url": (new URL(imgs[i].dataset.image, document.location.href)).href, "preset": imgs[i].dataset.preset });
							imgs[i]['data-position'] = i;
							imgs[i].addEventListener('click', function(click_event) {
								click_event.preventDefault();
								e.source.postMessage({ 'stereopix_action': 'goto', 'position': this['data-position'] }, 'https://stereopix.net');
							});
						}
						e.source.postMessage({ 'stereopix_action': 'list_add_json', 'media': json }, 'https://stereopix.net');
					} else if (e.data.type == 'mediumChanged') {
						imgs[last_active].classList.remove('active');
						last_active = e.data.position;
						imgs[last_active].classList.add('active');
					}
				}
			});
		</script>

		<iframe title="Stereoscopic (3D) photo viewer" id="stereopix_viewer"
			style="width: 100%; height: 960px; max-height: 100vh; max-width: 100vw; border: 2px solid black; margin: 8px 0;" 
			allowfullscreen="yes" allowvr="yes" allow="fullscreen;xr-spatial-tracking;accelerometer;gyroscope" 
			src="https://stereopix.net/viewer:embed/"></iframe>

            <p style="color:#9cf"><b>Note:</b> <i>Certaines photos du HAUM sont en relief, c'est pourquoi la visionneuse de Stereopix est utilisée. Si vous n'avez pas de dispositif pour observer en relief, choisissez le mode d'affichage "Single view left".</i></p>
                """)
        f.write('		<div class="thumbnails">\n')
        for photo in sorted(photos, key=lambda x: x['date'], reverse=True):
            create_thumbnail(album, photo['photo'])
            create_smallimg(album, photo['photo'])
            imgtype = 'video' if photo['video'] else 'image'
            imgpath = photo['photo'].replace('.mp4.jpg', '.mp4') if photo['video'] else photo['photo']
            f.write(f'''           <img src="../../thumbs/{ album }/{ photo['photo'] }" data-{ imgtype }="{ imgpath }" data-preset="{ photo['preset'] }" alt="" />\n''')
        f.write("""		</div>
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
                .albums {
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                }
                .albums > div {
                  width: 440px;
                  height: 210px;
                  border: solid 1px black;
                  background: #222;
                  padding: 10px;
                  margin: 10px;
                  text-align: center;
                }
                .albums > div div {
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
            <div class="albums">
    """)
        for album in sorted(albums, key=lambda x: x['date'], reverse=True):
            print(album)
            create_album_page(album['album'])
            f.write('           <div><a href="' + photosdirname + '/' + album['album'] + '/"><div><img src="' + thumbsdirname + '/' + album['album'] + '/' + album['thumb'] + '" /></div><div>' + html.escape(album['title']) + '</div></a></div>\n')
        f.write("""        </div>
        </body>
    </html>
    """) 

    create_index()

    # End
    bot.msg('Site de photos à jour.')
