# 文件: backend/apps/data_import/corpus_service.py
import os
from typing import Tuple

from django.conf import settings
from django.db.models import Q, QuerySet

from .models import CorpusData
from .services import parse_content
from .statistics import ALLOWED_TYPES, build_stats  # 统一来源
from .tasks import parse_corpus_task


class CorpusService:
    upload_dir = "uploads"

    def list_queryset(self, query: str = "", file_type: str = "", status: str = "") -> QuerySet:
        qs = CorpusData.objects.all().order_by("-id")
        if file_type:
            qs = qs.filter(fileType=file_type)
        if status:
            qs = qs.filter(status=status)
        if query:
            qs = qs.filter(
                Q(content__icontains=query) |
                Q(original_filename__icontains=query)
            )
        return qs

    def create_from_upload(self, up_file) -> Tuple[CorpusData, bool]:
        if not up_file:
            raise ValueError("缺少文件字段 file")
        original = up_file.name
        ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
        if ext not in ALLOWED_TYPES:
            raise ValueError(f"不支持的文件类型: {ext}")

        sync_mode = os.getenv("SYNC_PARSE", "0") == "1"

        obj = CorpusData.objects.create(
            fileType=ext,
            original_filename=original,
            content="" if not sync_mode else "（同步解析中...）",
            status="解析中" if not sync_mode else "已解析"
        )

        if sync_mode:
            file_bytes = up_file.read()
            try:
                content = parse_content(ext, file_bytes)
                obj.content = content
                obj.status = "已解析" if not content.startswith("解析失败") else "解析失败"
            except Exception as e:
                obj.content = f"解析失败：{e}"
                obj.status = "解析失败"
            obj.save(update_fields=["content", "status"])
            return obj, True

        base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        save_dir = os.path.join(base_dir, self.upload_dir)
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{obj.id}_{original}")
        with open(file_path, "wb") as f:
            for chunk in up_file.chunks():
                f.write(chunk)

        try:
            parse_corpus_task.delay(obj.id, ext, file_path)
        except Exception:
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                content = parse_content(ext, file_bytes)
                obj.content = content
                obj.status = "已解析" if not content.startswith("解析失败") else "解析失败"
                obj.save(update_fields=["content", "status"])
                return obj, True
            except Exception as e:
                obj.content = f"解析失败：{e}"
                obj.status = "解析失败"
                obj.save(update_fields=["content", "status"])
                return obj, True
        return obj, False

    def delete(self, pk: int):
        try:
            obj = CorpusData.objects.get(pk=pk)
        except CorpusData.DoesNotExist:
            raise ValueError("未找到")
        obj.delete()

    def stats(self):
        # 去重：直接复用 build_stats 作为唯一统计实现
        return build_stats()


# 单例
corpus_service = CorpusService()
