from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CorpusData
from .statistics import build_stats


def _broadcast_stats():
    channel_layer = get_channel_layer()
    counts = build_stats()["counts"]
    async_to_sync(channel_layer.group_send)(
        "global_stats",
        {
            "type": "stats_event",
            "payload": {
                "event": "stats.update",
                "stats": {"counts": counts},
            },
        },
    )


def _broadcast_corpus(event: str, instance: CorpusData, include_content: bool = True):
    channel_layer = get_channel_layer()
    payload = {
        "event": event,
        "data": {
            "id": instance.id,
            "fileType": instance.fileType,
            "status": instance.status,
        },
    }
    if include_content and instance.content:
        payload["data"]["content"] = instance.content
    async_to_sync(channel_layer.group_send)(
        "corpus_stream",
        {
            "type": "corpus_event",
            "payload": payload,
        },
    )


@receiver(post_save, sender=CorpusData)
def corpus_saved(sender, instance: CorpusData, created, **kwargs):
    _broadcast_corpus("corpus.created" if created else "corpus.updated", instance,
                      include_content=bool(instance.content))
    _broadcast_stats()


@receiver(post_delete, sender=CorpusData)
def corpus_deleted(sender, instance: CorpusData, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "corpus_stream",
        {
            "type": "corpus_event",
            "payload": {
                "event": "corpus.deleted",
                "data": {"id": instance.id},
            },
        },
    )
    _broadcast_stats()
