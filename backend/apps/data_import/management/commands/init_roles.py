from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "初始化基础角色分组：admin / annotator / viewer"

    def handle(self, *args, **options):
        created = 0
        for name in ["admin", "annotator", "viewer"]:
            _, was_created = Group.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"角色初始化完成，新建 {created} 个分组。"))
