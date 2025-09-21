from .models import CorpusData

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'json'}


def build_stats():
    counts = {t: 0 for t in ALLOWED_TYPES}
    for row in CorpusData.objects.values('fileType'):
        ft = row['fileType']
        if ft in counts:
            counts[ft] += 1
    total = sum(counts.values())
    return {
        "counts": counts,
        "total": total
    }
