# This file defines the database structure for our application.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings # Use settings to reference the User model

class User(AbstractUser):
    """
    Custom User Model. We add a user_type field to distinguish
    between Entrepreneurs and Investors.
    """
    USER_TYPE_CHOICES = (
        (1, 'entrepreneur'),
        (2, 'investor'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, null=True, blank=True)

class EntrepreneurProfile(models.Model):
    """
    Profile for the Entrepreneur user type.
    This model has a one-to-one relationship with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='entrepreneur_profile')
    company_name = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    funding_sought = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    business_plan = models.TextField(blank=True, help_text="Provide a detailed business plan.")
    company_details = models.TextField(blank=True, null=True, help_text="Detailed information about your company, mission, and team.")
    
    def __str__(self):
        return f"{self.user.username}'s Entrepreneur Profile"

class InvestorProfile(models.Model):
    """
    Profile for the Investor user type.
    This model also has a one-to-one relationship with the User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='investor_profile')
    investment_interests = models.CharField(max_length=255, blank=True, help_text="e.g., Technology, Healthcare, etc.")
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    past_investments = models.TextField(blank=True, help_text="List any notable past investments.")

    def __str__(self):
        return f"{self.user.username}'s Investor Profile"
    
# --- Pitch Model ---

class Pitch(models.Model):
    """
    Represents a business pitch created by an entrepreneur.
    """
    entrepreneur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pitches')
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=500, help_text="A short, compelling summary of your business.")
    details = models.TextField(help_text="Full details of your business pitch.")
    funding_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="How much funding are you asking for?")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'"{self.title}" by {self.entrepreneur.username}'
    
# --- Offer Model ---
class Offer(models.Model):
    """
    Represents an investment offer made by an investor on a pitch.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name='offers')
    investor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers_made')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    message = models.TextField(blank=True, help_text="Include a personal message or terms with your offer.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Offer of ${self.amount} for "{self.pitch.title}" by {self.investor.username}'

# --- Q&A Models ---
class Question(models.Model):
    """
    A question asked by an investor on a specific pitch.
    """
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE, related_name='questions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions_asked')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.author.username} on '{self.pitch.title}'"

class Answer(models.Model):
    """
    An answer provided by the entrepreneur to a question.
    """
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers_given')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.author.username} to question ID {self.question.id}"
