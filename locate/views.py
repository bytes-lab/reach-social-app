from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import UserProfile, UserNotification, UserRate, UserReport, UserFeed, UserRequest, UserInfinityBan, ChatContacts, ContactReq, PushNotification
from locate.models import Groups
from users.serializers import UserSerializer, UserReportSerializer, UserFeedSerializer, UserRequestSerializer, ChatContactsSerializer, ContactReqSerializer, PushNotificationSerializer

from reach.settings import APNS_CERF_PATH, APNS_CERF_SANDBOX_MODE, FEED_PAGE_OFFSET

from utils import send_email

import re
import json
import urllib2
from base64 import b64decode

from apns import APNs, Payload


@api_view(["POST"])
def create_group(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "group_title": "group title", 
        "group_bio": "group detail", 
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
		token = get_object_or_404(Token, key=request.data["token"])
                user = get_object_or_404(User, pk=token.user_id)
		groups = Groups.objects.create(creator=user, group_title=request.data["group_title"], group_bio=request.data["group_bio"])
		groups.save()
                return Response({"success": 20})
            else:
                return Response({"error": 17})
