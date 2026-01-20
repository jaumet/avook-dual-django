import json
import os
from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from .models import ChatSession, ChatMessage
from .services import get_openai_response

# A sensible default if the setting is not configured
CHATBOT_MAX_MESSAGES_PER_DAY = getattr(settings, 'CHATBOT_MAX_MESSAGES_PER_DAY', 50)

@csrf_exempt
@require_POST
@login_required
def chat_api(request):
    """
    Handles a user's chat message.

    This endpoint implements the main chat logic:
    1. Validates the user's daily message limit.
    2. Retrieves or creates a chat session.
    3. Saves the user's message.
    4. Calls the OpenAI service to get a response.
    5. Saves the assistant's response.
    6. Returns the assistant's message.
    """
    try:
        data = json.loads(request.body)
        user_message_content = data.get('message')
        if not user_message_content:
            return HttpResponseBadRequest("Missing 'message' in request body.")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON format.")

    # 1. Enforce daily message limit
    user = request.user
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    user_message_count = ChatMessage.objects.filter(
        session__user=user,
        role='user',
        created_at__gte=start_of_day
    ).count()

    if user_message_count >= CHATBOT_MAX_MESSAGES_PER_DAY:
        return HttpResponseForbidden("You have reached your daily message limit.")

    # 2. Get or create a chat session.
    # A new session is created if the user's last message in any session
    # is older than 1 hour.
    one_hour_ago = timezone.now() - timedelta(hours=1)

    latest_session = ChatSession.objects.filter(user=user).order_by('-created_at').first()

    if latest_session and latest_session.messages.exists() and latest_session.messages.latest('created_at').created_at > one_hour_ago:
        session = latest_session
    else:
        session = ChatSession.objects.create(user=user)

    # 3. Save the user's message
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message_content
    )

    # 4. Construct context and get OpenAI response
    try:
        assistant_response_content = get_openai_response(user, user_message_content, session)
    except Exception as e:
        # In a real app, log this error properly
        print(f"Error calling OpenAI service: {e}")
        return JsonResponse({'error': 'There was an error communicating with the chatbot service.'}, status=500)

    # 5. Save the assistant's message
    ChatMessage.objects.create(
        session=session,
        role='assistant',
        content=assistant_response_content
    )

    # 6. Return the response
    return JsonResponse({'reply': assistant_response_content})
