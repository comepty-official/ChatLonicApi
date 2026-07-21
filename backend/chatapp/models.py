from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (DECLINED, "Declined"),
    ]

    sender = models.ForeignKey(
        User,
        related_name="sent_requests",
        on_delete=models.CASCADE,
    )

    receiver = models.ForeignKey(
        User,
        related_name="received_requests",
        on_delete=models.CASCADE,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"


class Conversation(models.Model):
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name="messages",
        on_delete=models.CASCADE,
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    edited = models.BooleanField(default=False)

    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender}: {self.text[:25]}"