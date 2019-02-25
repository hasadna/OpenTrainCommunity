from django.contrib.postgres.fields import JSONField
from django.db import models


class Story(models.Model):
    dump = JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    last_saved_at = models.DateTimeField(auto_now=True)
    checksum = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return f'Story #{self.pk}'

    class Meta:
        verbose_name_plural = 'Stories'
        verbose_name = 'Story'
        ordering = ('-created_at', )


