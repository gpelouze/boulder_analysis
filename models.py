#!/usr/bin/env python3

import warnings

class PictureCrop():
    def __init__(self, ejson_crop):
        ejson_crop = ejson_crop.copy()
        self.x = ejson_crop.pop('x')
        self.y = ejson_crop.pop('y')
        self.width = ejson_crop.pop('width')
        self.height = ejson_crop.pop('height')
        if ejson_crop:
            warnings.warn('unparsed ejson_crop attributes')
            self.ejson_crop = ejson_crop

class Picture():
    def __init__(self, ejson_picture):
        ejson_picture = ejson_picture.copy()
        self.id = ejson_picture.pop('id')
        self.ratio = ejson_picture.pop('ratio')
        self.width = ejson_picture.pop('width')
        self.zoom_id = ejson_picture.pop('zoom')
        self.crop = PictureCrop(ejson_picture.pop('crop'))
        if ejson_picture:
            warnings.warn('unparsed ejson_picture attributes')
            self.ejson_picture = ejson_picture

    @property
    def src(self):
        return '{self.host}/800/bouldersPics/{self.id}.jpg'.format(**locals())

    @property
    def url(self):
        return '{self.host}/bouldersPics/{self.id}.jpg'.format(**locals())

    @property
    def zoom(self):
        return '{self.host}/bouldersZooms/{self.zoom_id}.jpg'.format(**locals())
