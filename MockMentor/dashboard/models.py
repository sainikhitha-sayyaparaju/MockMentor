from djongo import models
from gridfs_storage.storage import GridFSStorage


class Interview(models.Model):
    topic = models.CharField(max_length=30)
    subtopic = models.CharField(max_length=30, default='not required')
    expertise = models.CharField(max_length=30)
    number = models.IntegerField(default=10)


class Video(models.Model):
    first_pic = models.ImageField(storage=GridFSStorage(
        location='sample/images'))


