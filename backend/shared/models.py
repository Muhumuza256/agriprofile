import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model providing UUID primary key, created_at, and updated_at
    for every model in the platform.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
