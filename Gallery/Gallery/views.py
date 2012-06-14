from django.template import RequestContext
from django.shortcuts import render_to_response, render, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from Gallery.models import Album, Picture, Image, CommentForm

from os import walk
from ConfigParser import ConfigParser

# Config file where all settings for the gallery is stored.
# This has to be fqpn because you don't know where this script will run from.
CONFIG_FILE = '/var/django/photos_moshwire_com/Gallery/Gallery-settings.conf'

def albumIndex(request): # {{{
    '''Function returns the main page with all Album objects defined in db.'''
    
    return render_to_response(
        'Gallery/albumIndex.html',
        {
            'request': request,
            'options': getSettings(CONFIG_FILE, 'Options'),
            'albums': Album.objects.all().order_by('album_id')
        },
        context_instance = RequestContext(request)
    )

# }}}

def pictureIndex(request, albumName): # {{{
    '''Function returns all pictures defined in an album together with a template.'''

    options = getSettings(CONFIG_FILE, 'Options')
    requestedAlbum = get_object_or_404(Album, name = albumName.replace('_', ' '))
    requestedPictures = get_list_or_404(Picture, album_id = requestedAlbum)

    return render_to_response(
        'Gallery/pictureIndex.html', 
        {
            'request': request,
            'options': options,
            'requestedAlbum': requestedAlbum,
            'requestedPictures': requestedPictures 
        },
        context_instance = RequestContext(request)
    )

# }}}

def showPicture(request, albumName, fileName): # {{{
    '''Function returns the picture asked for together with the template.'''
    
    options = getSettings(CONFIG_FILE, 'Options')
    (requestedAlbum, requestedPicture) = getAlbumAndPictureOr404(albumName, fileName)
    
    return render_to_response(
        'Gallery/showPicture.html',
        {
            'request': request,
            'options': options,
            'forms': CommentForm(),
            'requestedAlbum': requestedAlbum,
            'requestedPicture': requestedPicture
        },
        context_instance = RequestContext(request)

) # }}} 

def redirectHome(request): return HttpResponseRedirect('/')

@login_required(login_url = '/log_in/')
def updateDB(request): # {{{
    '''Function updates the DB by adding or deleting rows depending on what
    albums it can find in the media folder and then redirecting the user to
    root url.
    '''
    
    options = getSettings(CONFIG_FILE, 'Options')
    (albumsInDB, albumsInMediaFolder) = albumsState(options['media'], Album.objects.all())
    
    for album in albumsInDB:
        if album not in albumsInMediaFolder and album != '':
            deleteAlbum = Album.objects.get(name = album)
            deleteAlbum.delete()
            
    for album in albumsInMediaFolder:
        if album not in albumsInDB:
            newAlbum = Album(path = album + '/', name = album)
            newAlbum.save()
            addPictures(newAlbum)
            
    return HttpResponseRedirect('/')

# }}}

@login_required(login_url = '/log_in/')
def updateComment(request, albumName, fileName): # {{{

    (requestedAlbum, requestedPicture) = getAlbumAndPictureOr404(albumName, fileName)
    
    if request.method == 'POST':
        form = CommentForm(request.POST) 
        if form.is_valid():
            requestedPicture.comment = form.cleaned_data['comment']
            requestedPicture.save()
            
    return HttpResponseRedirect('/' + albumName + '/' + fileName)

# }}} 

@login_required(login_url = '/log_in/')
def rotate(request, albumName, fileName, angle): # {{{
    
    if (int(angle) % 90) == 0:

        options = getSettings(CONFIG_FILE, 'Options')
        (requestedAlbum, requestedPicture) = getAlbumAndPictureOr404(albumName, fileName)
    
        image = Image(options['media'] + requestedAlbum.path + requestedPicture.filename, options)
        image.rotate(angle)
        image.save()
        image.resize()
        image.save(type = 'MS')
        image.thumbnail()
        image.save(type = 'T')

    return HttpResponseRedirect('/' + albumName)
    
# }}}

def logOut(request): # {{{
    logout(request)
    return HttpResponseRedirect('/')
# }}} 

def albumsState(directory, albumObjects): # {{{
    '''Function returns a tuple containing two lists with albums 
    in DB and albums in media folder.
    '''
    
    albumsInMediaFolderOrig = walk(directory).next()[1]

    albumsInMediaFolder = []
    for folder in albumsInMediaFolderOrig:
        if folder[0] != '.':
            albumsInMediaFolder.append(folder)
    
    albumsInDatabase = []
    for albumObject in albumObjects:
        path = albumObject.path.rsplit('/')
        albumsInDatabase.append(path[0])
                
    return (albumsInDatabase, albumsInMediaFolder)

# }}}

def getSettings(configFile, section): # {{{
    '''Function returns a dictionary with all the options in the
    specified config file and section.
    '''
    
    config = ConfigParser()
    config.optionxform = str
    config.read(configFile)
    options = {} 
    
    for option in config.options(section):
        options[option] = config.get(section, option)
    
    return options

# }}}

def addPictures(album): # {{{

    options = getSettings(CONFIG_FILE, 'Options')
    dirPath, dirNames, files = walk(options['media'] + album.name).next()
    
    for pfile in files:
        # We do this to make sure that scaled images from prior is not added to the
        # gallery it self. Also this will prevent hidden files to be added to the
        # gallery.
        if pfile[:3] == 'MS_' or pfile[:2] == 'T_' or pfile[:1] == '.':
            continue
            
        # If the "image" is not able to open, then something is wrong or it is
        # probably not a picture and we just iterate to the next file.
        try:
            image = Image(dirPath + '/' + pfile, options)
        except IOError:
            continue
        
        picture = Picture(
            album_id = album,
            filename = pfile,
            img_format = image.format,
            mode = image.mode,
            size_x = image.size[0],
            size_y = image.size[1]
        )
        picture.save()
        
        maxSizeImage = image.resize()
        maxSizeImage.save(options['media'] + album.name + '/MS_' + picture.filename)
        image.thumbnail()
        image.save(options['media'] + album.name + '/T_' + picture.filename)
        
        if album.index_image_filename is None:
            album.index_image_filename = 'T_' + picture.filename
            album.save()
            
# }}}

def getAlbumAndPictureOr404(albumName, fileName): # {{{

    requestedAlbum = get_object_or_404(Album, name = albumName.replace('_', ' '))
    requestedPicture = get_object_or_404(Picture, filename = fileName, album_id = requestedAlbum)
    
    return (requestedAlbum, requestedPicture)

# }}}

# vim: ai: syntax=python bg=dark ts=5 smarttab et sw=4 foldmethod=marker commentstring=#\ %s :
