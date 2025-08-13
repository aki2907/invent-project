# This file registers our models with the Django admin interface,
# so we can easily view and manage them.

from django.contrib import admin
from .models import User, EntrepreneurProfile, InvestorProfile, Pitch, Offer, Question, Answer

admin.site.register(User)
admin.site.register(EntrepreneurProfile)
admin.site.register(InvestorProfile)
admin.site.register(Pitch)
admin.site.register(Offer)
admin.site.register(Question) # Register Question
admin.site.register(Answer)   # Register Answer
