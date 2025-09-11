# We need to create this file. It will contain the forms for our application.
# Django forms handle rendering HTML form elements and validating user input.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, EntrepreneurProfile, InvestorProfile
from .models import Pitch
from .models import Offer
from .models import Question, Answer

class EntrepreneurSignUpForm(UserCreationForm):
    """
    A form for entrepreneurs to sign up. It includes fields from the User model
    and the EntrepreneurProfile model.
    """
    company_name = forms.CharField(max_length=255, required=True, help_text='Your company or startup name.')
    industry = forms.CharField(max_length=100, required=True, help_text='e.g., "FinTech", "Healthcare Tech"')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        # First, save the User object.
        user = super().save(commit=False)
        user.user_type = 1  # Set user_type to 'entrepreneur'
        if commit:
            user.save()
            # Then, create and save the EntrepreneurProfile.
            profile = EntrepreneurProfile.objects.create(
                user=user,
                company_name=self.cleaned_data.get('company_name'),
                industry=self.cleaned_data.get('industry')
            )
        return user

class InvestorSignUpForm(UserCreationForm):
    """
    A form for investors to sign up.
    """
    investment_interests = forms.CharField(max_length=255, required=True, help_text='Comma-separated interests, e.g., "AI, SaaS, Clean Energy"')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        # Save the User object.
        user = super().save(commit=False)
        user.user_type = 2  # Set user_type to 'investor'
        if commit:
            user.save()
            # Create and save the InvestorProfile.
            profile = InvestorProfile.objects.create(
                user=user,
                investment_interests=self.cleaned_data.get('investment_interests')
            )
        return user
    
# --- Profile Editing Forms ---
class EntrepreneurProfileForm(forms.ModelForm):
    """
    Form for Entrepreneurs to edit their profile details.
    """
    class Meta:
        model = EntrepreneurProfile
        fields = ('company_name', 'company_logo', 'industry', 'funding_sought', 'business_plan', 'company_details')
        widgets = {
            'business_plan': forms.Textarea(attrs={'rows': 8}),
        }

class InvestorProfileForm(forms.ModelForm):
    """
    Form for Investors to edit their profile details.
    """
    class Meta:
        model = InvestorProfile
        fields = ('investment_interests', 'budget', 'past_investments')
        widgets = {
            'past_investments': forms.Textarea(attrs={'rows': 5}),
        }

# --- Pitch Form ---
class PitchForm(forms.ModelForm):
    """
    A form for entrepreneurs to create and submit a new pitch.
    """
    class Meta:
        model = Pitch
        fields = ('title', 'summary', 'details', 'funding_amount')
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'details': forms.Textarea(attrs={'rows': 8}),
        }

# --- Offer Form ---
class OfferForm(forms.ModelForm):
    """
    A form for investors to make an offer on a pitch.
    """
    class Meta:
        model = Offer
        fields = ('amount', 'message')
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4}),
        }

# --- Q&A Forms ---
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ask a clarifying question...'}),
        }
        labels = {
            'text': '', # Hide the label
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Provide your answer...'}),
        }
        labels = {
            'text': 'Your Answer',
        }