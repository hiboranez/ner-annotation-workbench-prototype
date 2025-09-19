from django.db import models
from django.utils import timezone


class CorpusData(models.Model):
    # 文件类型（小写：pdf/docx/txt/json），默认值为 'pdf'
    fileType = models.CharField(max_length=50, default='pdf')
    # 原始文件名，默认值为空字符串
    original_filename = models.CharField(max_length=255, default='')
    # 解析/存储的文本或占位说明，默认为空字符串
    content = models.TextField(blank=True, default='')
    # 状态，默认值为 '已解析'
    status = models.CharField(max_length=50, default='已解析')
    # 创建时间，默认值为当前时间
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)
