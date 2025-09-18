from django.db import models


class CorpusData(models.Model):
    fileType = models.CharField(max_length=50)
    content = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.id
