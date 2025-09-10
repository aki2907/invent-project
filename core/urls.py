# Create this file. It maps URLs to the views we created.

from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/entrepreneur/', views.entrepreneur_dashboard_view, name='entrepreneur_dashboard'),
    path('dashboard/investor/', views.investor_dashboard_view, name='investor_dashboard'),
    path('pitch/<int:pitch_id>/', views.pitch_detail_view, name='pitch_detail'),
    path('offer/<int:offer_id>/respond/<str:new_status>/', views.respond_to_offer_view, name='respond_to_offer'),
    path('chat/', include('chat.urls', namespace='chat')),
    path('answer/<int:question_id>/', views.submit_answer_view, name='submit_answer'),
    path('search/', views.search_results_view, name='search_results'),
]
