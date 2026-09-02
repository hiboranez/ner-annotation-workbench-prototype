# python
# 文件: `backend/apps/data_import/services.py`
import json
from io import BytesIO


def parse_content(ext: str, file_bytes: bytes, limit: int = 10000) -> str:
    try:
        if ext == "txt":
            return file_bytes.decode(errors="ignore")[:limit]
        if ext == "json":
            raw = file_bytes.decode(errors="ignore")
            try:
                parsed = json.loads(raw)
                return json.dumps(parsed, ensure_ascii=False)[:limit]
            except Exception:
                return raw[:limit]
        if ext == "pdf":
            import PyPDF2
            reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            if getattr(reader, "is_encrypted", False):
                try:
                    reader.decrypt("")
                except Exception:
                    return "解析失败：PDF已加密"
            out, total = [], 0
            for p in reader.pages:
                try:
                    t = p.extract_text() or ""
                except Exception:
                    t = ""
                t = t.strip()
                if not t:
                    continue
                remain = limit - total
                if remain <= 0:
                    break
                if len(t) > remain:
                    t = t[:remain]
                out.append(t)
                total += len(t)
                if total >= limit:
                    break
            return ("\n".join(out).strip() or "解析结果为空")[:limit]
        if ext == "docx":
            from docx import Document
            doc = Document(BytesIO(file_bytes))
            out, total = [], 0
            for para in doc.paragraphs:
                t = (para.text or "").strip()
                if not t:
                    continue
                remain = limit - total
                if remain <= 0:
                    break
                if len(t) > remain:
                    t = t[:remain]
                out.append(t)
                total += len(t)
                if total >= limit:
                    break
            return ("\n".join(out).strip() or "解析结果为空")[:limit]
        return "已上传文件（未解析预览）"
    except Exception as e:
        return f"解析失败：{e}"
