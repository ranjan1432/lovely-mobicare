from django.db import models


class ContactEnquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    subject = models.CharField(max_length=200)
    message = models.TextField()

    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact enquiries"

    def __str__(self):
        return f"{self.name} - {self.subject}"