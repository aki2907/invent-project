# This file contains the logic that handles requests and returns responses.
# We'll create views for signing up, logging in, logging out, and the home page.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    EntrepreneurSignUpForm, InvestorSignUpForm,
    EntrepreneurProfileForm, InvestorProfileForm,
    PitchForm, OfferForm, QuestionForm, AnswerForm
)
from .models import User, EntrepreneurProfile, InvestorProfile, Pitch, Offer, Question, Answer
from chat.models import Conversation
from django.db.models import Q # Add this import for complex queries
from django.views.generic import TemplateView

def home_view(request):
    """
    The main landing page.
    """
    # Get the 3 most recent pitches to feature on the homepage
    featured_pitches = Pitch.objects.select_related('entrepreneur__entrepreneur_profile').order_by('-created_at')[:3]
    
    context = {
        'featured_pitches': featured_pitches
    }
    return render(request, 'home.html', context)

def search_results_view(request):
    query = request.GET.get('q', '')
    pitches = Pitch.objects.none()  # Default to an empty queryset
    investors = User.objects.none() # Default to an empty queryset

    if query:
        # Search for pitches based on title, summary, company name, or industry
        pitches = Pitch.objects.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(entrepreneur__entrepreneur_profile__company_name__icontains=query) |
            Q(entrepreneur__entrepreneur_profile__industry__icontains=query)
        ).distinct()

        # Search for investors based on name or investment interests
        investors = User.objects.filter(
            user_type=2
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(investor_profile__investment_interests__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'pitches': pitches,
        'investors': investors,
    }
    return render(request, 'search_results.html', context)

def signup_view(request):
    """
    Handles registration for both user types.
    We check the URL for a 'user_type' parameter to determine which form to show.
    """
    user_type = request.GET.get('user_type')
    if user_type == 'investor':
        form = InvestorSignUpForm(request.POST or None)
    else:
        # Default to entrepreneur
        form = EntrepreneurSignUpForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        # Placeholder: redirect to a dashboard. We'll build this next.
        return redirect('home') 
    
    return render(request, 'signup.html', {'form': form, 'user_type': user_type})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # This now correctly redirects to the dashboard view
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    return redirect('home')

# --- Dashboard and Profile Views ---
@login_required
def dashboard_view(request):
    """
    Redirects user to their specific dashboard based on user_type.
    """
    if request.user.user_type == 1:
        return redirect('entrepreneur_dashboard')
    elif request.user.user_type == 2:
        return redirect('investor_dashboard')
    else:
        # Fallback for superusers or users without a type
        return redirect('home')

@login_required
def entrepreneur_dashboard_view(request):
    """
    Displays the entrepreneur's dashboard, profile form,
    a list of their pitches, and a form to create a new pitch.
    Handles profile updates.
    """
    profile, created = EntrepreneurProfile.objects.get_or_create(user=request.user)

    # Handle both forms on one page
    profile_form = EntrepreneurProfileForm(instance=profile)
    pitch_form = PitchForm()

    # Get all unanswered questions for this entrepreneur's pitches
    unanswered_questions = Question.objects.filter(pitch__entrepreneur=request.user, answer__isnull=True).order_by('-created_at')
    answer_form = AnswerForm()

    if request.method == 'POST':
        if 'save_profile' in request.POST:
            profile_form = EntrepreneurProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('entrepreneur_dashboard')
        elif 'submit_pitch' in request.POST:
            pitch_form = PitchForm(request.POST)
            if pitch_form.is_valid():
                pitch = pitch_form.save(commit=False)
                pitch.entrepreneur = request.user
                pitch.save()
                return redirect('entrepreneur_dashboard')

    my_pitches = Pitch.objects.filter(entrepreneur=request.user).order_by('-created_at')
    # Get all offers for this entrepreneur's pitches
    received_offers = Offer.objects.filter(pitch__entrepreneur=request.user).order_by('-created_at')
    # Get conversations
    my_conversations = Conversation.objects.filter(participants=request.user).order_by('-created_at')
        
    context = {
        'profile_form': profile_form,
        'pitch_form': pitch_form,
        'my_pitches': my_pitches,
        'received_offers': received_offers, # Add offers to context
        'my_conversations': my_conversations, # Add to context
        'unanswered_questions': unanswered_questions,
        'answer_form': answer_form,
    }
    return render(request, 'entrepreneur_dashboard.html', context)

@login_required
def investor_dashboard_view(request):
    """
    Displays the investor's dashboard with their profile form,
    a list of all available pitches from entrepreneurs
    and a list of their own sent offers.
    Handles profile updates.
    """
    profile, created = InvestorProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = InvestorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('investor_dashboard')
    else:
        form = InvestorProfileForm(instance=profile)

    # --- Search and Filter Logic ---
    all_pitches = Pitch.objects.select_related('entrepreneur__entrepreneur_profile').all().order_by('-created_at')
    
    search_query = request.GET.get('q', '')
    selected_industry = request.GET.get('industry', '')

    if search_query:
        all_pitches = all_pitches.filter(
            Q(title__icontains=search_query) |
            Q(summary__icontains=search_query) |
            Q(details__icontains=search_query)
        )
    
    if selected_industry:
        all_pitches = all_pitches.filter(entrepreneur__entrepreneur_profile__industry=selected_industry)

    # Get a list of unique industries for the filter dropdown
    industries = EntrepreneurProfile.objects.exclude(industry__exact='').values_list('industry', flat=True).distinct().order_by('industry')
    
    # --- Get all offers made by this specific investor ---
    offers_made = Offer.objects.filter(investor=request.user).select_related('pitch').order_by('-created_at')
    
    my_conversations = Conversation.objects.filter(participants=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'all_pitches': all_pitches,
        'my_conversations': my_conversations,
        'industries': industries,
        'search_query': search_query,
        'selected_industry': selected_industry,
        'offers_made': offers_made,
    }
    return render(request, 'investor_dashboard.html', context)


# --- Pitch Detail View ---
@login_required
def pitch_detail_view(request, pitch_id):
    """
    Displays the full details of a single pitch.
    Accessible by investors.
    """
    # Ensure only investors can view pitch details for now
    if request.user.user_type != 2: # Must be an investor
        return redirect('dashboard')

    pitch = get_object_or_404(Pitch, id=pitch_id)
    offer_form = OfferForm()
    question_form = QuestionForm()

    # Handle new question submission from an investor
    if 'submit_question' in request.POST and request.user.user_type == 2:
        q_form = QuestionForm(request.POST)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.pitch = pitch
            question.author = request.user
            question.save()
            return redirect('pitch_detail', pitch_id=pitch.id)

    # Handle offer submission (existing logic)
    if 'submit_offer' in request.POST and request.user.user_type == 2:
        o_form = OfferForm(request.POST)
        if o_form.is_valid():
            offer = o_form.save(commit=False)
            offer.pitch = pitch
            offer.investor = request.user
            offer.save()
            return redirect('investor_dashboard') # Redirect after making offer
        else:
            offer_form = o_form # Show errors if invalid

    # Check if this investor has already made an offer on this pitch
    existing_offer = Offer.objects.filter(pitch=pitch, investor=request.user).first()

    questions = pitch.questions.order_by('-created_at')

    context = {
        'pitch': pitch,
        'offer_form': offer_form,
        'existing_offer': existing_offer,
        'question_form': question_form,
        'questions': questions,
    }
    return render(request, 'pitch_detail.html', context)

# --- Views for Offer Actions ---
@login_required
def respond_to_offer_view(request, offer_id, new_status):
    """
    A single view to handle both accepting and rejecting an offer.
    """
    offer = get_object_or_404(Offer, id=offer_id)
    
    # Security check: ensure the logged-in user is the pitch owner
    if offer.pitch.entrepreneur != request.user:
        return HttpResponseForbidden("You are not authorized to respond to this offer.")
    
    # Validate the new status
    if new_status in ['accepted', 'rejected']:
        offer.status = new_status
        offer.save()
    
    # If accepted, create a new conversation
        if new_status == 'accepted':
            conversation, created = Conversation.objects.get_or_create(offer=offer)
            if created:
                conversation.participants.add(offer.pitch.entrepreneur, offer.investor)

    return redirect('entrepreneur_dashboard')

# --- NEW view for submitting an answer ---
@login_required
def submit_answer_view(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    # Security check: only the pitch owner can answer
    if request.user != question.pitch.entrepreneur:
        return HttpResponseForbidden("You are not authorized to answer this question.")

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
    
    return redirect('entrepreneur_dashboard')

# Views for static pages
class AboutView(TemplateView):
    template_name = 'about.html'

class HowItWorksView(TemplateView):
    template_name = 'how_it_works.html'
    
class ContactView(TemplateView):
    template_name = 'contact.html'

about_view = AboutView.as_view()
how_it_works_view = HowItWorksView.as_view()
contact_view = ContactView.as_view()