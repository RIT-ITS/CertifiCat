from django.db import models


class Config(models.Model):
    """
    A model to store key-value configuration settings.
    """

    key = models.CharField(
        max_length=255, unique=True, help_text="Unique key for the setting"
    )
    value = models.TextField(blank=True, help_text="Value of the setting")
    description = models.TextField(blank=True, help_text="Description of the setting")

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get(cls, key: str, default=None):
        """
        Retrieves a setting by its key.
        Returns default if the key is not found.
        """
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key: str, value: str, description=""):
        """
        Creates or updates a setting.
        """
        setting, _ = cls.objects.update_or_create(
            key=key, defaults={"value": value, "description": description}
        )
        return setting

    class Meta:
        verbose_name = "Configuration Setting"
        verbose_name_plural = "Configuration Settings"
        ordering = ["key"]  # noqa: RUF012
