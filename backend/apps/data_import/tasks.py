from celery import shared_task
from .models import CorpusData
from .services import parse_content


@shared_task(bind=True, max_retries=2)
def parse_corpus_task(self, corpus_id, ext, file_path):
    try:
        obj = CorpusData.objects.get(id=corpus_id)
    except CorpusData.DoesNotExist:
        return
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        content = parse_content(ext, file_bytes)
        obj.content = content
        obj.status = "已解析" if not content.startswith("解析失败") else "解析失败"
    except Exception as e:
        obj.content = f"解析失败：{e}"
        obj.status = "解析失败"
    obj.save(update_fields=["content", "status"])
