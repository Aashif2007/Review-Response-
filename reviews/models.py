
from django.db import models
from business.models import Business


class Review(models.Model):

    SENTIMENT = [
        ("Pending", "Pending"),
        ("Positive", "Positive"),
        ("Negative", "Negative"),
        ("Neutral", "Neutral"),
    ]

    # Business that owns this review
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE
    )

    # Customer information
    customer_name = models.CharField(
        max_length=100
    )

    rating = models.IntegerField()

    review_text = models.TextField()

    # AI sentiment
    sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT,
        default="Pending"
    )

    # AI-generated reply
    ai_reply = models.TextField(
        blank=True,
        null=True
    )

    # Reply edited by owner
    owner_reply = models.TextField(
        blank=True,
        null=True
    )

    # Final published reply
    published_reply = models.TextField(
        blank=True,
        null=True
    )

    # Approval status
    approved = models.BooleanField(
        default=False
    )

    # Spam detection
    spam = models.BooleanField(
        default=False
    )

    spam_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.customer_name
