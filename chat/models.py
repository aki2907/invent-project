from django.db import models
from django.conf import settings

class Conversation(models.Model):
    """
    A private conversation between an entrepreneur and an investor,
    usually linked to an accepted offer.
    """
    offer = models.OneToOneField('core.Offer', on_delete=models.CASCADE, related_name='conversation')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation for Offer on '{self.offer.pitch.title}'"

class Message(models.Model):
    """
    A single message within a conversation.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
    