from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Base model for all models in the project."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object by setting is_active to False."""
        self.is_active = False
        self.save()

    def restore(self):
        """Restore the object by setting is_active to True."""
        self.is_active = True
        self.save()

    def hard_delete(self):
        """Hard delete the object from the database."""
        super().delete()

    def save(self, *args, **kwargs):
        """Override save method to update updated_at field."""
        if not self.id:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs) 