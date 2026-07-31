from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Business(models.Model):

    BUSINESS_TYPES = [
        ('Hotel', 'Hotel'),
        ('Hostel', 'Hostel'),
        ('Restaurant', 'Restaurant'),
        ('Cafe', 'Cafe'),
        ('Clinic', 'Clinic'),
        ('Salon', 'Salon'),
        ('Gym', 'Gym'),
        ('Shop', 'Shop'),
        ('Other', 'Other'),
    ]

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    business_name = models.CharField(max_length=200)

    # Public, URL-safe identifier used for the customer-facing review
    # page, e.g. /b/my-hotel/. Generated automatically from the
    # business name the first time the business is saved.
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    business_type = models.CharField(
        max_length=50,
        choices=BUSINESS_TYPES
    )

    email = models.EmailField()

    phone = models.CharField(max_length=20)

    address = models.TextField()

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.business_name) or "business"
            slug = base_slug
            counter = 1

            while Business.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name
