from django import forms
from django.db import models
from os.path import split
from Image import open as Iopen, ANTIALIAS

class Album(models.Model): # {{{
    album_id = models.AutoField(primary_key = True)
    path = models.CharField(max_length = 200, unique = True)
    index_image_filename = models.CharField(max_length = 200, blank = True, null = True, default = None)
    name = models.CharField(max_length = 200)

    def __unicode__(self): return self.name

    def name_spaces_to_underscores(self): # {{{
        return self.name.replace(' ', '_')
    # }}}

    def name_underscores_to_spaces(self): # {{{
        return self.name.replace('_', ' ')
    # }}}

# }}}

class Picture(models.Model): # {{{
    picture_id = models.AutoField(primary_key = True)
    album_id = models.ForeignKey('album')
    filename = models.CharField(max_length = 200)
    img_format = models.CharField('format', max_length = 200)
    comment = models.CharField(max_length = 200, blank = True, null = True, default = None)
    mode = models.CharField(max_length = 200)
    size_x = models.IntegerField()
    size_y = models.IntegerField()

    def __unicode__(self): return self.filename

# }}}

class CommentForm(forms.Form): # {{{
    comment = forms.CharField(max_length = 200)
# }}}

class Image(): # {{{

    def __init__(self, fqpn, options): # {{{
        try:
            self.image = Iopen(fqpn)
        except IOError:
            raise

        (self.filePath, self.fileName) = split(fqpn)
        self.format = self.image.format
        self.mode = self.image.mode
        self.size = self.image.size
        self.options = options

    # }}}

    def __unicode__(self): return self.fileName

    def save(self, fqpn = None, type = None): # {{{
        if fqpn is not None:
            if type == 'MS':
                self.image.save(fqpn)
            elif type == 'T':
                self.image.save(fqpn)
            else: 
                self.image.save(fqpn)
        else:
            if type == 'MS':
                self.image.save(self.filePath + '/MS_' + self.fileName)
            elif type == 'T':
                self.image.save(self.filePath + '/T_' + self.fileName)
            else: 
                self.image.save(self.filePath + '/' + self.fileName)
    # }}}
    
    def resize(self): # {{{

        '''Method resizes the picture to the maximum allowed size if size in
        horisontal plane is bigger than maximum defined in config file.

        We do this because Gallery has limits in terms of estetics the horisontal
        way, but not in the vertical way.
        '''

        if int(self.size[0]) > int(self.options['maxsize']):

            # diffValue will make sure the aspect ratio is kept for the resize
            # We force result to be an int since we only want "whole" numbers.
            diffValue = self.size[0] / float(self.options['maxsize'])
            sizeHor = int(self.size[0] / diffValue)
            sizeVer = int(self.size[1] / diffValue)
        
            self.image = self.image.resize((sizeHor,sizeVer), ANTIALIAS)
            self.size = self.image.size
            return self.image

        return self.image

    # }}}

    def thumbnail(self): # {{{
        self.image.thumbnail(
            (
                int(self.options['thumbnailx']),
                int(self.options['thumbnaily'])
            ),
            ANTIALIAS
        )
        self.size = self.image.size
        return self.image
    # }}}

    def rotate(self, angle): # {{{
        self.image = self.image.rotate(int(angle))
        self.size = self.image.size
        return self.image
    # }}}

# }}}

# vim: ai: syntax=python bg=dark ts=4 smarttab et sw=4 foldmethod=marker commentstring=#\ %s :
