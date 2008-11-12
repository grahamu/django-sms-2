from django.contrib.contenttypes.models import ContentType
from django.db import models

class PhoneNumberManager(models.Manager):
    def get_for_user(self, user_obj):
        """
        Filter the ``QuerySet`` for a specific ``User``.
        
        ``user_obj`` should be ``django.contrib.auth.models.User``
        """
        
        user_ctype = ContentType.objects.get(app_label="auth", model="user")
        
        return self.filter(
            content_type = user_ctype,
            object_id = user_obj.pk
        )