from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Conversation

@login_required
def chat_room_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Security check: ensure user is a participant
    if request.user not in conversation.participants.all():
        return HttpResponseForbidden("You are not part of this conversation.")
        
    return render(request, 'chat/room.html', {'conversation': conversation})
