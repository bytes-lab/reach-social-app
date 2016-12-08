from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from posts.models import Post, Comment
from users.models import UserProfile, UserNotification, UserRate, UserReport, UserFeed, UserRequest, UserInfinityBan, ChatContacts, ContactReq, PushNotification
from circles.models import Circle
from users.serializers import UserSerializer, UserReportSerializer, UserFeedSerializer, UserRequestSerializer, ChatContactsSerializer, ContactReqSerializer, PushNotificationSerializer
from circles.serializers import CircleSerializer

from reach.settings import APNS_CERF_PATH, APNS_CERF_SANDBOX_MODE, FEED_PAGE_OFFSET, BASE_DIR

from utils import send_email

import re
import json
import urllib2
import datetime
from base64 import b64decode

import sendgrid
from sendgrid.helpers.mail import *

from apns import APNs, Payload
import facebook
import braintree
from mailchimp3 import MailChimp

from django.contrib.gis.geos import *
from django.contrib.gis.measure import D

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="k5n223gdbkt49kc6",
                                  public_key="6kjkyb6gknjbk6k9",
                                  private_key="2cef56043deef9273ba5fe21be10251a")

client = MailChimp('jason5001002', 'aa316c4894783a929c6b9bee8ed15740-us14')
sg = sendgrid.SendGridAPIClient(apikey='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')

@api_view(["POST"])
def registration(request):
    """
    User registration method.

        Example json:
        {
            "username":"antonboksha",
            "first_name": "Anton",
            "last_name": "Boksha",
            "birthday": "1987-12-27",
            "email":"antonboksha@gmail.com",
            "password":"qwerty",
            "device_token": "devicetokengoeshere",
            "device_unique_id": "devicegoeshere"
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "success": 1,
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "user": {
                "id": 3,
                "username": "antonboksha",
                "first_name": "Anton",
                "last_name": "Boksha",
                "email": "antonboksha@gmail.com",
                "info": {
                        "full_name": "Anton Boksha",
                        "biography": "My short biography here!",
                        "like_count": 13,
                        "comment_count": 27,
                        "rate": 3,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 1,
                "complete_likes": 50
            }
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    # username validation
    username = request.data.get('username')

    if not username:
        return

    if User.objects.filter(username=username).exists():
        return Response({"error": 2})
    if len(username) < 4:
        return Response({"error": 3})
    if len(username) > 20:
        return Response({"error": 4})
    if " " in username:
        return Response({"error": 5})
    if not re.match("^[a-zA-Z0-9_]\w{3,19}$", username):
        return Response({"error": 6})

    # email validation
    email = request.data.get('email', '').lower()
    if not email:
        return Response({"error": 8})
    if not re.match("^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$", email):
        return Response({"error": 8})
    if User.objects.filter(email=email).exists():
        return Response({"error": 7})

    # validate password
    password = request.data.get('password')
    if not password:
        return Response({"error": 9})        
    if len(password) < 6:
        return Response({"error": 9})
    if len(password) > 20:
        return Response({"error": 10})
    if " " in password:
        return Response({"error": 11})
    
    # check banned device
    device_unique_id = request.data.get('device_unique_id')
    if UserInfinityBan.objects.filter(device_unique_id=device_unique_id).exists():
        return Response({"error": 86})
    
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')

    if not (first_name and last_name):
        return Response({"error": 'First name and Last name should be provided.'})

    try:
        birthday = request.data.get('birthday')
        birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
    except Exception, e:
        return Response({"error": 'Birthday should be in YYYY-MM-DD format.'})

    # create a user
    user = User.objects.create(username=username, email=email, 
        first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.save()

    # send registration email    
    from_email = Email("test@example.com")
    subject = "Welcome to Reach Anonymous"
    to_email = Email(user.email)

    path = BASE_DIR + '/static/email_templates/signup.html'
    temp = open(path, 'r')
    content = temp.read().replace('[USERNAME]', user.first_name)
    content = Content("text/html", content)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    # create a token and userprofile
    token = Token.objects.create(user=user)
    up = UserProfile.objects.create(user=user, device_unique_id=device_unique_id,
        full_name="{} {}".format(first_name, last_name), birthday=birthday, rate=-1)
    # create a user notification
    device_token = request.data.get("device_token")
    if UserNotification.objects.filter(device_token=device_token).exists():
        UserNotification.objects.filter(device_token=device_token).delete()
        UserNotification.objects.create(user_id=token.user_id,
                                        device_token=device_token)
    else:
        UserNotification.objects.create(user_id=token.user_id,
                                        device_token=device_token)
        
    message = 'Welcome to Reach app!'
    serializer = UserSerializer(user)
    # send_email('Reach. Welcome!', message)
    # user.email_user('Reach. Welcome!', message)

    return Response({"success": 1,
                     "token": token.key,
                     "user": serializer.data})


@api_view(["POST"])
def login(request):
    """
    User login method.

        Example json:
        {
            "email":"antonboksha@gmail.com",
            "password":"qwerty",
            "device_token": "devicetokengoeshere",
            "device_unique_id": "devicegoeshere"
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "success": 12,
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "user": {
                "id": 3,
                "username": "antonboksha",
                "first_name": "Anton",
                "last_name": "Boksha",
                "email": "antonboksha@gmail.com",
                "info": {
                        "full_name": "Anton Boksha",
                        "biography": "My short biography here!",
                        "like_count": 13,
                        "comment_count": 27,
                        "rate": 3,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 1,
                "complete_likes": 50
            }
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        email = request.data.get('email', '').lower()
        password = request.data.get('password', '')
        device_unique_id = request.data.get("device_unique_id")

        if not User.objects.filter(email=email).exists():
            return Response({"error": 16})

        if UserInfinityBan.objects.filter(device_unique_id=device_unique_id).exists():
            return Response({"error": 86})

        user = get_object_or_404(User, email=email)
        token = get_object_or_404(Token, user=user)

        if user.check_password(password):
            if UserNotification.objects.filter(user_id=token.user_id).exists():
                UserNotification.objects.filter(user_id=token.user_id).delete()
                UserNotification.objects.create(user_id=token.user_id,
                                                device_token=request.data["device_token"])
            else:
                UserNotification.objects.create(user_id=token.user_id,
                                                device_token=request.data["device_token"])
                
            serializer = UserSerializer(user)
            return Response({"success": 12,
                             "token": token.key,
                             "user": serializer.data})
        else:
            return Response({"error": 14})


@api_view(["POST"])
def forgot_password(request):
    """
User recover password method.

    Example json:
    {
        "email":"antonboksha@gmail.com"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 15
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        email = request.data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                if re.match("^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$", email):
                    user = get_object_or_404(User, email=email)
                    new_password = User.objects.make_random_password()
                    user.set_password(new_password)
                    user.save()
                    # message = 'Your new password is: ' + new_password
                    # user.email_user('Reach. Your new password!', message)

                    # send registration email    
                    from_email = Email("test@example.com")
                    subject = "Reset Password"
                    to_email = Email(email)
                    
                    path = BASE_DIR + '/static/email_templates/new_password.html'
                    temp = open(path, 'r')
                    content = temp.read().replace('[USERNAME]', email).replace('[PASSWORD]', new_password)
                    content = Content("text/html", content)
                    mail = Mail(from_email, subject, to_email, content)
                    response = sg.client.mail.send.post(request_body=mail.get())

                    return Response({"success": 15})
                else:
                    return Response({"error": 8})
            else:
                return Response({"error": 16})


@api_view(["POST"])
def contactus(request):
    email = request.data.get('email')
    if email:
        if User.objects.filter(email=email).exists():
            if re.match("^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$", email):
                user = get_object_or_404(User, email=email)
                
                # send contact accepted email to user
                from_email = Email("test@example.com")
                subject = "Contact Accepted"
                to_email = Email(email)
                
                path = BASE_DIR + '/static/email_templates/contactus_user.html'
                temp = open(path, 'r')
                content = temp.read().replace('[USERNAME]', user.first_name)
                content = Content("text/html", content)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())

                # send contact accepted email to admin
                from_email = Email("test@example.com")
                subject = "Contact Request"
                to_email = Email('michaelgarevalo@gmail.com')
                
                path = BASE_DIR + '/static/email_templates/contactus_admin.html'
                temp = open(path, 'r')
                content = temp.read().replace('[EMAIL]', user.email)
                content = Content("text/html", content)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())

                return Response({"success": 15})
            else:
                return Response({"error": 8})
    return Response({"error": 16})


@api_view(["POST"])
def get_user_by_id(request):
    """
    Get user by id method.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "user_id": 1
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "user": {
                "id": 1,
                "username": "antonboksha",
                "first_name": "Anton",
                "last_name": "Boksha",
                "email": "antonboksha@gmail.com",
                "info": {
                    "full_name": "Anton Boksha",
                    "biography": "My short biography here!",
                    "like_count": 13,
                    "comment_count": 27,
                    "rate": 3,
                    "avatar": "/media/default_images/default.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 1,
                "complete_likes": 50
            },
            "success": 20
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        token = request.data.get('token')
        user_id = request.data.get('user_id')
        if Token.objects.filter(key=token).exists():
            if type(user_id) is int:
                user = get_object_or_404(User, pk=user_id)
                serializer = UserSerializer(user)
                return Response({"success": 20, "user": serializer.data})
            return Response({"error": 18})
        return Response({"error": 17})


@api_view(["POST"])
def get_user_by_token(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 1,
            "username": "antonboksha",
            "first_name": "Anton",
            "last_name": "Boksha",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "Anton Boksha",
                "biography": "My short biography here!",
                "like_count": 13,
                "comment_count": 27,
                "rate": 3,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
        "success": 20
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                user = get_object_or_404(User, pk=token.user_id)
                serializer = UserSerializer(user)
                return Response({"success": 20,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def change_email(request):
    """
Change user email

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "email": "qwe@gmail.com"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 1,
            "username": "antonboksha",
            "first_name": "Anton",
            "last_name": "Boksha",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "Anton Boksha",
                "biography": "My short biography here!",
                "like_count": 13,
                "comment_count": 27,
                "rate": 3,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
        "success": 20
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
        if Token.objects.filter(key=request.data["token"]).exists():
            token = get_object_or_404(Token, key=request.data["token"])
            user = get_object_or_404(User, pk=token.user_id)
            if User.objects.filter(email=request.data["email"]).exists():
                return Response({"error": 7})
            else:
                user.email = request.data["email"]
                user.save()

                # send success email    
                from_email = Email("test@example.com")
                subject = "Reach Email Chage"
                to_email = Email(user.email)

                path = BASE_DIR + '/static/email_templates/new_email.html'
                temp = open(path, 'r')
                content = temp.read().replace('[USER]', user.first_name)
                content = Content("text/html", content)
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())

                serializer = UserSerializer(user)
                return Response({"success": 20,
                                 "user": serializer.data})
        else:
            return Response({"error": 17})


@api_view(["POST"])
def change_password(request):
    """
Change user password.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "old_password": "qwerty",
        "new_password": "qwerty_new"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 1,
            "username": "antonboksha",
            "first_name": "Anton",
            "last_name": "Boksha",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "Anton Boksha",
                "biography": "My short biography here!",
                "like_count": 13,
                "comment_count": 27,
                "rate": 3,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
        "success": 13
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                user = get_object_or_404(User, pk=token.user_id)

                auth_user = authenticate(username=user.username, password=request.data['old_password'])
                if auth_user is not None:
                    if "new_password" in request.data and request.data["new_password"] != "" \
                                and request.data["new_password"] is not None:
                        if len(request.data["new_password"]) < 6:
                            return Response({"error": 9})
                        elif len(request.data["new_password"]) > 20:
                            return Response({"error": 10})
                        elif " " in request.data["new_password"]:
                            return Response({"error": 11})
                        else:
                            user.set_password(request.data['new_password'])
                            user.save()
                            serializer = UserSerializer(user)
                            return Response({"success": 60,
                                             "user": serializer.data})
                else:
                    return Response({"error": 14})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def change_bio(request):
    """
Change user bio.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "biography": "Are you really programmer?"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 1,
            "username": "antonboksha",
            "first_name": "Anton",
            "last_name": "Boksha",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "Anton Boksha",
                "biography": "My short biography here!",
                "like_count": 13,
                "comment_count": 27,
                "rate": 3,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
        "success": 13
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                user = get_object_or_404(User, pk=token.user_id)
                user_profile = get_object_or_404(UserProfile, user_id=token.user_id)
                user_profile.biography = request.data["biography"]
                user_profile.save()
                serializer = UserSerializer(user)
                return Response({"success": 61,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_user_profile_by_token(request):
    """
Get full user profile by token

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circles": [
            {
                "id": 1,
                "name": "qwe",
                "owner": {
                    "id": 2,
                    "username": "antonboksha",
                    "first_name": "",
                    "last_name": "",
                    "email": "antonboksha@gmail.com",
                    "info": {
                        "full_name": "",
                        "biography": "qweqweqwe",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 0,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    },
                    "count_downvoted": 1,
                    "count_upvoted": 1,
                    "count_likes": 1,
                    "count_comments": 1,
                    "complete_likes": 50
                },
                "description": "asd",
                "permission": true,
                "image": "/media/circle/e4c2c9be-9356-454a-afff-514df03940e2.jpg",
                "group": {
                    "id": 1,
                    "name": "sex",
                    "count_circles": 1
                },
                "members_count": 1,
                "join": false,
                "topics": [
                    {
                        "id": 1,
                        "author": {
                            "id": 2,
                            "username": "antonboksha",
                            "first_name": "",
                            "last_name": "",
                            "email": "antonboksha@gmail.com",
                            "info": {
                                "full_name": "",
                                "biography": "qweqweqwe",
                                "like_count": 0,
                                "comment_count": 0,
                                "rate": 0,
                                "avatar": "/media/default_images/default.png",
                                "is_facebook": false,
                                "is_twitter": false,
                                "is_instagram": false
                            },
                            "count_downvoted": 1,
                            "count_upvoted": 1,
                            "count_likes": 1,
                            "count_comments": 1,
                            "complete_likes": 50
                        },
                        "text": "some problem here",
                        "permission": true,
                        "date": "2016-02-02T14:16:59.161082Z",
                        "replies": [
                            {
                                "id": 1,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:44:10.029647Z"
                            },
                            {
                                "id": 2,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:52:15.435364Z"
                            },
                            {
                                "id": 3,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:52:34.359412Z"
                            }
                        ]
                    }
                ]
            }
        ],
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 0,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
        "success": 62
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    user = get_object_or_404(User, pk=token.user_id)
                    user_serializer = UserSerializer(user)
                    circles = Circle.objects.filter(owner=user)
                    circles_serializer = CircleSerializer(circles, many=True)
                    return Response({"success": 62,
                                     "user": user_serializer.data,
                                     "circles": circles_serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_user_profile_by_id(request):
    """
Get full user profile by user_id and token.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circles": [
            {
                "id": 1,
                "name": "qwe",
                "owner": {
                    "id": 2,
                    "username": "antonboksha",
                    "first_name": "",
                    "last_name": "",
                    "email": "antonboksha@gmail.com",
                    "info": {
                        "full_name": "",
                        "biography": "qweqweqwe",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 0,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    },
                    "count_downvoted": 1,
                    "count_upvoted": 1,
                    "count_likes": 1,
                    "count_comments": 1,
                    "complete_likes": 50
                },
                "description": "asd",
                "permission": true,
                "image": "/media/circle/e4c2c9be-9356-454a-afff-514df03940e2.jpg",
                "group": {
                    "id": 1,
                    "name": "sex",
                    "count_circles": 1
                },
                "members_count": 1,
                "join": false,
                "topics": [
                    {
                        "id": 1,
                        "author": {
                            "id": 2,
                            "username": "antonboksha",
                            "first_name": "",
                            "last_name": "",
                            "email": "antonboksha@gmail.com",
                            "info": {
                                "full_name": "",
                                "biography": "qweqweqwe",
                                "like_count": 0,
                                "comment_count": 0,
                                "rate": 0,
                                "avatar": "/media/default_images/default.png",
                                "is_facebook": false,
                                "is_twitter": false,
                                "is_instagram": false
                            },
                            "count_downvoted": 1,
                            "count_upvoted": 1,
                            "count_likes": 1,
                            "count_comments": 1,
                            "complete_likes": 50
                        },
                        "text": "some problem here",
                        "permission": true,
                        "date": "2016-02-02T14:16:59.161082Z",
                        "replies": [
                            {
                                "id": 1,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:44:10.029647Z"
                            },
                            {
                                "id": 2,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:52:15.435364Z"
                            },
                            {
                                "id": 3,
                                "author": {
                                    "id": 2,
                                    "username": "antonboksha",
                                    "first_name": "",
                                    "last_name": "",
                                    "email": "antonboksha@gmail.com",
                                    "info": {
                                        "full_name": "",
                                        "biography": "qweqweqwe",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    },
                                    "count_downvoted": 1,
                                    "count_upvoted": 1,
                                    "count_likes": 1,
                                    "count_comments": 1,
                                    "complete_likes": 50
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:52:34.359412Z"
                            }
                        ]
                    }
                ]
            }
        ],
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 0,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 1,
            "complete_likes": 50
        },
	"is_friend" : 0/1/2,   0: default 1: friend 2: already requested 
        "success": 62
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
		    token = get_object_or_404(Token, key=request.data["token"])
                    user = get_object_or_404(User, pk=request.data["user_id"])
                    user_serializer = UserSerializer(user)

                    circles = Circle.objects.filter(owner=user)
                    circles_serializer = CircleSerializer(circles, many=True)

		    isFriend = 0
		    isContactReq = ContactReq.objects.filter(Q(user_id=token.user_id) | Q(otheruser_id=token.user_id)).count()
		    if isContactReq > 0:
		    	isFriend = 2
		    isContact = ChatContacts.objects.filter(user_id=token.user_id, otheruser_id=request.data["user_id"]).count()
		    if isContact > 0:
			isFriend = 1
                    return Response({"success": 62,
                                     "user": user_serializer.data,
                                     "circles": circles_serializer.data, "is_friend": isFriend})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def rate_user(request):
    """
Rate user.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1,
        "rate": 1,
        "message": "hello"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 10,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 2,
            "complete_likes": 50
        },
        "success": 67
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    user_profile = get_object_or_404(UserProfile, user_id=request.data["user_id"])
                    user_profile.count_rates += 1
                    user_profile.rate += request.data["rate"]
                    user_profile.save()
                    user = get_object_or_404(User, pk=request.data["user_id"])
                    user_rate = UserRate.objects.create(sender_id=token.user_id,
                                                        receiver_id=request.data["user_id"],
                                                        message=request.data["message"],
                                                        rate=request.data["rate"])
                    serializer = UserSerializer(user)
                    UserFeed.objects.create(user_rate=user_rate,
                                            action="Feedback",
                                            user=user,
                                            action_user=token.user)
                    message = "{} leave a feedback about you".format(token.user.username)
                    custom = {
                        "user": serializer.data
                    }
                    token.user.email_user('Reach. Feedback!', message)
                    apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
                    payload = Payload(alert=message, sound="default", category="TEST", badge=1, custom=custom)
                    user_notifications = UserNotification.objects.filter(user=user_rate.receiver)
                    for user_notification in user_notifications:
                        try:
                            apns.gateway_server.send_notification(user_notification.device_token, payload)
                        except:
                            pass
                    return Response({"success": 67,
                                     "user": serializer.data})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def change_avatar(request):
    """
Change user avatar.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "avatar": "base64string"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 10,
                "avatar": "/media/default_images/default.png",
                "is_facebook": false,
                "is_twitter": false,
                "is_instagram": false
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 2,
            "complete_likes": 50
        },
        "success": 68
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                user_profile = get_object_or_404(UserProfile, user_id=token.user_id)
                image_data = b64decode(request.data['avatar'])
                user_profile.avatar = ContentFile(image_data, 'whatup.png')
                user_profile.save()
                user = get_object_or_404(User, pk=token.user_id)
                serializer = UserSerializer(user)
                return Response({"success": 68,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def report_user(request):
    """
Report user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 69
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    if UserReport.objects.filter(user_id=token.user_id, reported_id=request.data["user_id"]).exists():
                        return Response({"error": 70})
                    else:
                        UserReport.objects.create(user_id=token.user_id, reported_id=request.data["user_id"])
                        return Response({"success": 69})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def check_report_user_by_token(request):
    """
Check report user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 71
        "reported": True
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    if UserReport.objects.filter(user_id=token.user_id, reported_id=request.data["user_id"]).exists():
                        return Response({"success": 71,
                                         "reported": True})
                    else:
                        return Response({"success": 71,
                                         "reported": False})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def check_report_user_by_id(request):
    """
Check report user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 71
        "reported": True
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    if UserReport.objects.filter(user_id=request.data["user_id"], reported_id=token.user_id).exists():
                        return Response({"success": 71,
                                         "reported": True})
                    else:
                        return Response({"success": 71,
                                         "reported": False})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_reported_users(request):
    """
Get list of reported users

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "reports": [
            {
                "id": 1,
                "reported": {
                    "id": 3,
                    "username": "test2",
                    "first_name": "",
                    "last_name": "",
                    "email": "qwe@qwe.qwe",
                    "info": null,
                    "count_downvoted": 0,
                    "count_upvoted": 0,
                    "count_likes": 0,
                    "count_comments": 0,
                    "complete_likes": 0
                },
                "date": "2016-03-30T12:58:54.921794Z"
            }
        ],
        "success": 71
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                reports = UserReport.objects.filter(user_id=token.user_id)
                serializer = UserReportSerializer(reports, many=True)
                return Response({"success": 72,
                                 "reports": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def send_report_email(request):
    """
Send report email to admin
Please send only one parameter:
   - `post_id`(for Post object report)
   - `comment_id`(for PostComment object report)
   - `circle_id`(for Circle object report)

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "post_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 73
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                if 'post_id' in request.data:
                    if Post.objects.filter(pk=request.data["post_id"]).exists():
                        post = get_object_or_404(Post, pk=request.data["post_id"])
                        content = 'New report email from {}(id: {}) about POST: "{}" ' \
                                  '(post-id: {}). Post author {}(id: {})'.format(token.user.email,
                                                                                 token.user.id,
                                                                                 post.text[:50],
                                                                                 post.id,
                                                                                 post.author.email,
                                                                                 post.author.id)
                    else:
                        return Response({"error": 27})
                elif 'comment_id' in request.data:
                    if Comment.objects.filter(pk=request.data["comment_id"]).exists():
                        comment = get_object_or_404(Comment, pk=request.data["comment_id"])
                        content = 'New report email from {}(id: {}) about COMMENT: "{}" ' \
                                  '(comment-id: {}). Comment author {}(id: {})'.format(token.user.email,
                                                                                       token.user.id,
                                                                                       comment.text[:50],
                                                                                       comment.id,
                                                                                       comment.author.email,
                                                                                       comment.author.id)
                    else:
                        return Response({"error": 35})
                elif 'circle_id' in request.data:
                    if Circle.objects.filter(pk=request.data["circle_id"]).exists():
                        circle = get_object_or_404(Circle, pk=request.data["circle_id"])
                        content = 'New report email from {}(id: {}) about CIRCLE: "{}" ' \
                                  '(circle-id: {}). Circle creator {}(id: {})'.format(token.user.email,
                                                                                      token.user.id,
                                                                                      circle.name[:50],
                                                                                      circle.id,
                                                                                      circle.owner.email,
                                                                                      circle.owner.id)
                    else:
                        return Response({"error": 51})
                subject = 'New report. Please check it.'
                send_email(subject=subject, content=content)
                return Response({"success": 73})

            else:
                return Response({"error": 17})


@api_view(["POST"])
def remove_reported_user(request):
    """
Remove reported user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 69
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    if UserReport.objects.filter(user_id=token.user_id, reported_id=request.data["user_id"]).exists():
                        report = get_object_or_404(UserReport,
                                                   user_id=token.user_id,
                                                   reported_id=request.data["user_id"])
                        report.delete()
                        return Response({"success": 74})
                    else:
                        return Response({"error": 75})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_user_feed(request):
    """
Get User Feed

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "offset": 0
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "feed": [
            {
                "id": 1,
                "action_user": {
                    "id": 4,
                    "username": "antonsdfboksha",
                    "first_name": "",
                    "last_name": "",
                    "email": "antonbosdfsdfksha@gmail.com",
                    "info": {
                        "full_name": "",
                        "biography": "",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 1,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    },
                    "count_downvoted": 0,
                    "count_upvoted": 0,
                    "count_likes": 0,
                    "count_comments": 0,
                    "complete_likes": 0
                },
                "action": "PostComment",
                "object": 1,
                "date": "2016-04-02T16:40:05.836267Z"
            }
        ],
        "success": 76,
        "offset": 10
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                start_offset = request.data["offset"]
                end_offset = start_offset + FEED_PAGE_OFFSET
                feed = UserFeed.objects.filter(user=token.user).exclude(action_user=token.user).order_by("-date")[start_offset:end_offset]
                serializer = UserFeedSerializer(feed, many=True)
                return Response({"success": 76,
                                 "feed": serializer.data,
                                 "offset": end_offset})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def send_direct_request(request):
    """
Send direct request to user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1, 
	"fromuser_id": 12
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "request": {
            "id": 2,
            "user": {
                "id": 2,
                "username": "antonboksha",
                "first_name": "",
                "last_name": "",
                "email": "antonboksha@gmail.com",
                "info": {
                    "full_name": "",
                    "biography": "qweqweqwe",
                    "like_count": 0,
                    "comment_count": 0,
                    "rate": 7,
                    "avatar": "/media/userprofile/849d5d9c-e968-4c7c-b96c-23aa46a719fd.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 6,
                "complete_likes": 50
            },
            "allow": false,
            "date": "2016-04-03T11:50:02.935707Z"
        },
        "success": 77
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
		    fromuser = get_object_or_404(User, pk=request.data["fromuser_id"])
                    user = get_object_or_404(User, pk=request.data["user_id"])
                    user_request = UserRequest.objects.create(user=fromuser,
                                                              request_user=user)
                    serializer = UserRequestSerializer(user_request)
                    UserFeed.objects.create(user=user,
                                            action_user=fromuser,
                                            action="Request",
                                            user_request=user_request)
                    return Response({"success": 77,
                                     "request": serializer.data})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def allow_direct_request(request):
    """
Allow direct request to user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "request_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "request": {
            "id": 2,
            "user": {
                "id": 2,
                "username": "antonboksha",
                "first_name": "",
                "last_name": "",
                "email": "antonboksha@gmail.com",
                "info": {
                    "full_name": "",
                    "biography": "qweqweqwe",
                    "like_count": 0,
                    "comment_count": 0,
                    "rate": 7,
                    "avatar": "/media/userprofile/849d5d9c-e968-4c7c-b96c-23aa46a719fd.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 6,
                "complete_likes": 50
            },
            "allow": true,
            "date": "2016-04-03T11:50:02.935707Z"
        },
        "success": 78
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if UserRequest.objects.filter(pk=request.data["request_id"]).exists():
                    user_request = get_object_or_404(UserRequest, pk=request.data["request_id"])
                    user_request.allow = True
                    user_request.save()
                    serializer = UserRequestSerializer(user_request)
                    message = "{} allow your request".format(user_request.request_user.username)
                    custom = {
                        "request": serializer.data
                    }
                    apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
                    payload = Payload(alert=message, sound="default", category="TEST", badge=1, custom=custom)
                    user_notifications = UserNotification.objects.filter(user=user_request.user)
                    for user_notification in user_notifications:
                        try:
                            apns.gateway_server.send_notification(user_notification.device_token, payload)
                        except:
                            pass
                    get_object_or_404(UserFeed, user_request=user_request).delete()
                    return Response({"success": 78,
                                     "request": serializer.data})
                else:
                    return Response({"error": 79})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def check_direct_request(request):
    """
Check direct request status (true/false)

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "request_status": true,
        "success": 80
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                if UserRequest.objects.filter(user=token.user, request_user_id=request.data["user_id"]).exists():
                    user_request = get_object_or_404(UserRequest,
                                                     user=token.user,
                                                     request_user_id=request.data["user_id"])
                    return Response({"success": 80,
                                     "request_status": user_request.allow})
                else:
                    return Response({"error": 79})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def start_call(request):
    """
Send push before start call

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1,
        "permission": True
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 81
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    if request.data["permission"]:
                        message = "{} is calling you right now".format(token.user.username)
                        custom = {
                            "full_name": "{} {}".format(token.user.first_name,
                                                        token.user.last_name)
                        }
                    else:
                        message = "Anonymous is calling you right now"
                        custom = {
                            "full_name": "Anonymous"
                        }

                    apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
                    payload = Payload(alert=message, sound="default", category="TEST", badge=1, custom=custom)
                    user_notifications = UserNotification.objects.filter(user_id=request.data["user_id"])
                    for user_notification in user_notifications:
                        try:
                            apns.gateway_server.send_notification(user_notification.device_token, payload)
                        except:
                            pass
                    return Response({"success": 81})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def send_message(request):
    """
Send message push

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "user_id": 1
        "message": "Die, insect!"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 82
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if User.objects.filter(pk=request.data["user_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    message = "{}: {}".format(token.user.username,
                                              request.data["message"][:20])
                    custom = {
                        "message": request.data["message"],
                        "sender_id": token.user_id
                    }
                    apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
                    payload = Payload(alert=message, sound="default", category="TEST", badge=1, custom=custom)
                    user_notifications = UserNotification.objects.filter(user_id=request.data["user_id"])
                    for user_notification in user_notifications:
                        try:
                            apns.gateway_server.send_notification(user_notification.device_token, payload)
                        except:
                            pass
                    return Response({"success": 82})
                else:
                    return Response({"error": 19})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def connect_facebook(request):
    """
Connect facebook account to user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "access_token": "sometokengoeshere"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 7,
                "avatar": "/media/userprofile/849d5d9c-e968-4c7c-b96c-23aa46a719fd.png",
                "is_facebook": true,
                "is_twitter": true,
                "is_instagram": false,
                "facebook_url": "https://www.facebook.com/app_scoped_user_id/1168737826510483",
                "twitter_url": "https://twitter.com/durov",
                "instagram_url": ""
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 6,
            "complete_likes": 50
        },
        "success": 83
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                graph = facebook.GraphAPI(access_token=request.data["access_token"], timeout=60)
                facebook_user = graph.get_object("me", fields='id, name, email, first_name, last_name, '
                                                              'picture.type(large), bio, birthday, gender, '
                                                              'hometown, about')
                user_profile = get_object_or_404(UserProfile, user=token.user)
                user_profile.is_facebook = True
                user_profile.facebook_url = "https://www.facebook.com/app_scoped_user_id/{}".format(facebook_user["id"])
                user_profile.save()
                user = get_object_or_404(User, pk=token.user_id)
                serializer = UserSerializer(user)
                return Response({"success": 83,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def connect_twitter(request):
    """
Connect twitter account to user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "screen_name": "durov"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 7,
                "avatar": "/media/userprofile/849d5d9c-e968-4c7c-b96c-23aa46a719fd.png",
                "is_facebook": true,
                "is_twitter": true,
                "is_instagram": false,
                "facebook_url": "https://www.facebook.com/app_scoped_user_id/1168737826510483",
                "twitter_url": "https://twitter.com/durov",
                "instagram_url": ""
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 6,
            "complete_likes": 50
        },
        "success": 84
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                user_profile = get_object_or_404(UserProfile, user=token.user)
                user_profile.is_twitter = True
                user_profile.twitter_url = "https://twitter.com/{}".format(request.data["screen_name"])
                user_profile.save()
                user = get_object_or_404(User, pk=token.user_id)
                serializer = UserSerializer(user)
                return Response({"success": 84,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def connect_instagram(request):
    """
Connect facebook account to user

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "access_token": "sometokengoeshere"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "user": {
            "id": 2,
            "username": "antonboksha",
            "first_name": "",
            "last_name": "",
            "email": "antonboksha@gmail.com",
            "info": {
                "full_name": "",
                "biography": "qweqweqwe",
                "like_count": 0,
                "comment_count": 0,
                "rate": 7,
                "avatar": "/media/userprofile/849d5d9c-e968-4c7c-b96c-23aa46a719fd.png",
                "is_facebook": true,
                "is_twitter": true,
                "is_instagram": false,
                "facebook_url": "https://www.facebook.com/app_scoped_user_id/1168737826510483",
                "twitter_url": "https://twitter.com/durov",
                "instagram_url": ""
            },
            "count_downvoted": 1,
            "count_upvoted": 1,
            "count_likes": 1,
            "count_comments": 6,
            "complete_likes": 50
        },
        "success": 83
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                url = 'https://api.instagram.com/v1/users/self/?access_token=%s' % request.data["access_token"]
                obj = json.loads(urllib2.urlopen(url).read().decode('utf8'))

                user_profile = get_object_or_404(UserProfile, user=token.user)
                user_profile.is_instagram = True
                user_profile.instagram_url = "https://www.instagram.com/{}/".format(obj["data"]["username"])
                user_profile.save()
                user = get_object_or_404(User, pk=token.user_id)
                serializer = UserSerializer(user)
                return Response({"success": 85,
                                 "user": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def read_user_feed(request):
    """
Read all user feed

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 89
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                feed = UserFeed.objects.filter(user=token.user,
                                               read=False)
                for single_feed in feed:
                    single_feed.read = True
                    single_feed.save()
                return Response({"success": 89})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def count_unread_user_feed(request):
    """
Count unread user feed

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 90,
        "unread_count": 12
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                unread_count = UserFeed.objects.filter(user=token.user,
                                                       read=False).count()
                return Response({"success": 90,
                                 "unread_count": unread_count})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def status_code(request):
    """
    Status codes:

        1 - registration successfully
        2 - user with this username is already exist
        3 - username is less than 4 symbols
        4 - username is more than 20 symbols
        5 - username contain space(s)
        6 - username contain special character(s)
        7 - user with this email is already exist
        8 - email is not in format like qwe@qwe.qwe
        9 - password is less that 6 symbols
        10 - password is more that 20 symbols
        11 - password contain space(s)
        12 - login successfully
        13 - successfully change password
        14 - incorrect password
        15 - recover password successfully
        16 - user with this email doesn't exist
        17 - token doesn't exist
        18 - user_id is not integer
        19 - user with this id doesn't exist
        20 - getting user successfully
        21 - post text is less than 1 symbol
        22 - post text is more than 10000 symbols
        23 - successfully add new post
        24 - comment text is less that 10 symbols
        25 - comment text is more that 255 symbols
        26 - successfully add new comment
        27 - post with this post_id doesn't exist
        29 - successfully get user posts
        30 - successfully send like
        31 - you already like this post
        32 - post with that ID doesn't exist
        33 - successfully remove like
        34 - you haven't like this post yet
        35 - comment with that ID doesn't exist
        36 - this is not your comment, can't remove
        37 - successfully remove comment
        38 - successfully send like/dislike to this comment
        39 - you already like/dislike this comment
        40 - you successfully change the best_response status
        41 - you don't have permissions to mark comment as best response
        42 - circle name must be more than 4 symbols
        43 - circle name must be less than 50 symbols
        44 - circle description must be more that 4 symbols
        45 - circle description must be less than 500 symbols
        46 - circle with that name is already exist
        47 - successfully create a new circle
        48 - successfully get all circles
        49 - successfully get all created circles
        50 - successfully get all joined circles
        51 - circle with that id doesn't exist
        52 - successfully get single circle
        53 - you can't create a new topic in this circle(you aren't a member)
        54 - successfully join/unjoin circle
        55 - successfully created a new topic in circle
        56 - successfully get single topic
        57 - topic with that id doesn't exist
        58 - successfully get all groups
        59 - group with that id doesn't exist
        60 - successfully change password
        61 - successfully change biography
        62 - successfully get user profile
        63 - successfully get explore-popular
        64 - successfully get explore-daily-upvotes
        65 - successfully get explore-most-upvoted
        66 - successfully search by hashtag
        67 - successfully rate user
        68 - successfully change user avatar
        69 - successfully add user to your report list
        70 - you already report this user
        71 - successfully check report user
        72 - successfully get reported users list
        73 - successfully send report email
        74 - successfully remove user from your report list
        75 - this user not in your report list
        76 - successfully get user feed
        77 - successfully send direct request
        78 - successfully allow request
        79 - request with that id doesn't exist
        80 - successfully check request status
        81 - successfully send push "start call"
        82 - successfully send push "new message"
        83 - successfully connect facebook account
        84 - successfully connect twitter account
        85 - successfully connect instagram account
        86 - you are banned
        87 - successfully get single post
        88 - post with that id doesn't exist
        89 - successfully read user feed
        90 - successfully count user unread feed
        91 - successfully remove post
    """
    return Response({"status": "code"})


@api_view(["POST"])
def update_locate(request):
    """
    Update User locate.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "country_name": "United States",
            "state_name": "Kensington",
            "city_name": "New York",
            "latitude": 0.0,
            "longitude": 0.0
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "success": 13
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        token = request.data.get('token')
        if token:
            if Token.objects.filter(key=token).exists():
                token = get_object_or_404(Token, key=token)
                user = get_object_or_404(User, pk=token.user_id)
                user_profile = get_object_or_404(UserProfile, user_id=token.user_id)
                user_profile.country_name = request.data["country_name"]
                user_profile.state_name = request.data.get('state_name', 'New york')
                user_profile.city_name = request.data["city_name"]
                user_profile.latitude = request.data["latitude"]
                user_profile.longitude = request.data["longitude"]
                user_profile.location = Point(x=request.data["latitude"], 
                    y=request.data["longitude"], z=0, srid=4326)

                if user_profile.rate == -1:
                    # first call after registration
                    user_profile.rate = 0

                    client.lists.members.create('81f38aba85', {
                        'email_address': user.email,
                        'status': 'subscribed', #subscribed unsubscribed cleaned pending
                        'merge_fields': {
                            'FNAME': user.first_name,
                            'LNAME': user.last_name,
                            'BIRTHDAY': datetime.datetime.strftime(user_profile.birthday, '%m/%d/%Y'),
                            'CITY': user_profile.city_name, 
                            'STATE': user_profile.state_name,
                            'COUNTRY': user_profile.country_name
                        },
                    })

                user_profile.save()
                serializer = UserSerializer(user)
                return Response({"success": 61})
        return Response({"error": 17})


@api_view(["POST"])
def get_user_nearby(request):
    """
Update User locate.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "latitude": 0.0,
        "longitude": 0.0
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "success": 13
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
		user = User.objects.all()
		serializer = UserSerializer(user,  many=True, context={'user_id': token.user_id})
                return Response({"success": 61,
				"user": serializer.data})
            else:
		return Response({"error": 17})


@api_view(["POST"])
def get_user_by_name(request):
    """
    Get user by token method.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df", 
            "username" : ""
        }
    """
    if request.method == "POST":
        token = request.data.get('token')
        if Token.objects.filter(key=token).exists():
            user = get_object_or_404(User, username=request.data["username"])
            serializer = UserSerializer(user)
            return Response({"success": 20, "user": serializer.data})
        return Response({"error": 17})


@api_view(["POST"])
def search_user_by_name(request):
    """
    Get user by token method.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df", 
            "username" : ""
        }
    """
    if request.method == "POST":
        token = get_object_or_404(Token, key=request.data.get("token"))
        user = User.objects.filter(username__contains=request.data["username"]).exclude(pk=token.user_id)
        if user:
            serializer = UserSerializer(user, many=True)
            return Response({"success": 20, "user": serializer.data})
        return Response({"error": 17})


@api_view(["POST"])
def contact_request(request):
    """
    Get user by token method.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df", 
            "user_id" : , 
            "other_userid" :
        }
    """
    if request.method == "POST":
        token = request.data.get('token')
        if Token.objects.filter(key=token).exists():
            token = get_object_or_404(Token, key=token)
            reqUser = get_object_or_404(User, pk=request.data["user_id"])
            reqOtherUser = get_object_or_404(User, pk=request.data["other_userid"])

            contactReq = ContactReq.objects.create(user=reqUser, 
                otheruser=reqOtherUser)
            return Response({"success": 20})

        return Response({"error": 17})


@api_view(["POST"])
def get_contact_request(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                contactRequest=ContactReq.objects.filter(otheruser_id=token.user_id)

                serializer = ContactReqSerializer(contactRequest, many=True)
                return Response({"success": 20,
                                 "request": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def delete_contact_request(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
	"contactreq_id" : 5
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
                ContactReq.objects.filter(pk=request.data["contactreq_id"]).delete()
		
                contactRequest=ContactReq.objects.filter(otheruser_id=token.user_id)
		serializer = ContactReqSerializer(contactRequest, many=True)
                return Response({"success": 20,
                                 "request": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def accept_contact_request(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "otheruser_id" : 3,
        "contactreq_id" : 5
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
		ContactReq.objects.filter(pk=request.data["contactreq_id"]).delete()
		
		userParam = get_object_or_404(User, pk=token.user_id)		
		otherParam = get_object_or_404(User, pk=request.data["otheruser_id"])
		chatContacts = ChatContacts.objects.create(user=userParam, 
						 	   otheruser_id=request.data["otheruser_id"],
							   favourite_type=0)
		otherContacts = ChatContacts.objects.create(user=otherParam,
							   otheruser_id=token.user_id,
							   favourite_type=0)
		chatContacts.save()		
		otherContacts.save()	
		
                contactRequest=ContactReq.objects.filter(otheruser_id=token.user_id)
                serializer = ContactReqSerializer(contactRequest, many=True)
                return Response({"success": 20,
                                 "request": serializer.data})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_contacts(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df"
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                token = get_object_or_404(Token, key=request.data["token"])
		
		chatContacts = ChatContacts.objects.filter(user=token.user_id)
                serializer = ChatContactsSerializer(chatContacts, many=True)
                return Response({"success": 20,
                                 "request": serializer.data})
            else:
                return Response({"error": 17})

@api_view(["POST"])
def uget_user_by_token(request):
    """
    Get user by token method.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df", 
            "qbchat_id" : 234
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "user": {
                "id": 1,
                "username": "antonboksha",
                "first_name": "Anton",
                "last_name": "Boksha",
                "email": "antonboksha@gmail.com",
                "info": {
                    "full_name": "Anton Boksha",
                    "biography": "My short biography here!",
                    "like_count": 13,
                    "comment_count": 27,
                    "rate": 3,
                    "avatar": "/media/default_images/default.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                },
                "count_downvoted": 1,
                "count_upvoted": 1,
                "count_likes": 1,
                "count_comments": 1,
                "complete_likes": 50
            },
            "success": 20
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        token = request.data.get('token')
        if token:
            if Token.objects.filter(key=token).exists():
                token = get_object_or_404(Token, key=token)
                user = get_object_or_404(User, pk=token.user_id)
                user_profile = get_object_or_404(UserProfile, user_id=token.user_id)
                user_profile.qbchat_id = request.data["qbchat_id"]
                user_profile.save()
                serializer = UserSerializer(user)
                return Response({"success": 20,
                                 "user": serializer.data})
        return Response({"error": 17})


@api_view(["POST"])
def get_password_by_ID(request):
    """
Change user password.

    Example json:
    {
        "user_id": 12
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
                user = get_object_or_404(User, pk=request.data["user_id"])
                return Response({"success": 60,
                                 "user": user.password})
    else:
                return Response({"error": 17})


@api_view(["POST"])
def send_notification(request):
    """
Send push notification.

    Example json:
    {	
        "user_id": 12, 
	"fromuser_id": 17,
	"message" : "alert message", 
	"sound" : "default",
	"custom" : "custom_data", 
	"category" : "call_category"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
		apns = APNs(use_sandbox=True, cert_file=APNS_CERF_PATH)
		
		custom = request.data["custom"]

                user_notifications = UserNotification.objects.filter(user=request.data["user_id"])
		user = get_object_or_404(User, pk=request.data["user_id"])
		fromuser_id = get_object_or_404(User, pk=request.data["fromuser_id"])
                for user_notification in user_notifications:
			pushNotification = PushNotification.objects.create(user=user,
									 fromuser=fromuser_id,
									 alert_type=custom["type"], 
									 reading_type=0, 
									 alert=request.data["message"], 
									 sound=request.data["sound"], 
									 category=request.data["category"], 
									 custom=json.dumps(custom))
                        pushNotification.save()
                return Response({"success": 60})
    else:
                return Response({"error": 17})


@api_view(["GET"])
def task_notification(request):
    """
Automatically send notification.

    Example json:
    {   
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "GET":
                apns = APNs(use_sandbox=True, cert_file=APNS_CERF_PATH)
		pushNotifications = PushNotification.objects.filter(reading_type=0)
		if pushNotifications.count() == 0:
			return Response({"error": 17})
		for pushNotification in pushNotifications:
			userID = pushNotification.user_id
			custom = json.loads(pushNotification.custom)
			notifications = PushNotification.objects.filter(user=userID).count()
			payload = Payload(alert=pushNotification.alert, sound=pushNotification.sound, category=pushNotification.category, badge=notifications, custom=custom)
                	user_notifications = UserNotification.objects.filter(user=userID)
	                for user_notification in user_notifications:
                        	try:
	                            apns.gateway_server.send_notification(user_notification.device_token, payload)
				    pushNotification.reading_type = 1
				    pushNotification.save()
			           
				    if (pushNotification.alert_type == 1) or (pushNotification.alert_type == 0):
					pushNotification.delete()
        	                except:
                	            pass
                return Response({"success": 60, "userID": userID})
    else:
                return Response({"error": 17})

@api_view(["POST"])
def delete_chat_notification(request):
    """
Delete Chat Notification.

    Example json:
    {   
        "user_id": 12,
	"fromuser_id": 17, 
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
		if PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"], fromuser=request.data["fromuser_id"]).exists():
			pushNotifications = PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"], fromuser=request.data["fromuser_id"])
			if pushNotifications.count() == 0:
				return Response({"error": 79})
	                for pushNotification in pushNotifications:
        	                pushNotification.delete()
		
			chat_badge = PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"]).count()
			contact_request_badge = PushNotification.objects.filter(reading_type=1, alert_type=3, user=request.data["user_id"]).count()
			contact_accept_badge = PushNotification.objects.filter(reading_type=1, alert_type=4, user=request.data["user_id"]).count()
                        return Response({"success": 60,
                                         "chat_badge": chat_badge,
                                         "contact_req_badge": contact_request_badge, 
					 "contact_accept_badge": contatct_accept_badge})

		else:
			return Response({"error": 79})
    else:
                return Response({"error": 79})




@api_view(["POST"])
def delete_notifications(request):
    """
Delete Chat Notification.

    Example json:
    {   
        "user_id": 12,
        "alert_type": 3 
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
                if PushNotification.objects.filter(reading_type=1, alert_type=request.data["alert_type"], user=request.data["user_id"]).exists():
                        pushNotifications = PushNotification.objects.filter(reading_type=1, alert_type=request.data["alert_type"], user=request.data["user_id"])
                        if pushNotifications.count() == 0:
                                return Response({"error": 79})
                        for pushNotification in pushNotifications:
                                pushNotification.delete()
			
			if PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"]).exists():
	                        chat_badge = PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"]).count()
			else:
				chat_badge = 0
			contact_request_badge = PushNotification.objects.filter(reading_type=1, alert_type=3, user=request.data["user_id"]).count()
			contact_accept_badge = PushNotification.objects.filter(reading_type=1, alert_type=4, user=request.data["user_id"]).count()
        		return Response({"success": 60,
                       		     	 "chat_badge": chat_badge,
                            	 	 "contact_req_badge": contact_request_badge, 
					 "contact_accept_badge": contact_accept_badge})

                else:
                        return Response({"error": 79})
    else:
                return Response({"error": 79})


@api_view(["POST"])
def get_notification_badge(request):
    """
Delete Chat Notification.

    Example json:
    {   
        "user_id": 12
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
    }
    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
                chat_badge = PushNotification.objects.filter(reading_type=1, alert_type=2, user=request.data["user_id"]).count()
		contact_request_badge = PushNotification.objects.filter(reading_type=1, alert_type=3, user=request.data["user_id"]).count()
		contact_accept_badge = PushNotification.objects.filter(reading_type=1, alert_type=4, user=request.data["user_id"]).count()
                return Response({"success": 60, 
				 "chat_badge": chat_badge, 
				 "contact_req_badge": contact_request_badge, 
				 "contact_accept_badge": contact_accept_badge})
    else:
                return Response({"error": 17})


@api_view(["POST"])
def client_token(request):
	return Response({"success": 60, 
			 "client_token": braintree.ClientToken.generate()})


@api_view(["POST"])
def create_purchase(request):
	nonce_from_the_client = request.data["payment_method_nonce"]
	result = braintree.Transaction.sale({
    					     "amount": "10.00",
				    	     "payment_method_nonce": nonce_from_the_client,
    					     "options": {
	  					    	"submit_for_settlement": True
						    	}
					   })
	return Response({"success": 60, 
	                 "result": result})


@api_view(["POST"])
def get_contact_accept_notification(request):
    """
    Get Contact Accept Chat Notification.

        Example json:
        {   
            "user_id": 12
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "success": 60, 
            "result": []
        }
        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        user_id = request.data["user_id"]
        pn = pushNotifications = PushNotification.objects.filter(reading_type=1, 
            alert_type=4, user=user_id)
        if pn:
            result = PushNotificationSerializer(pn, many=True)			
            return Response({"success": 60, "result": result.data})
        return Response({"error": 79})


@api_view(["POST"])
def unfriend_task(request):
    """
Get user by token method.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
	"user_id": 12, 
	"otheruser_id": 17
    }


    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                chatContacts = ChatContacts.objects.filter(Q(user=request.data["user_id"], otheruser=request.data["otheruser_id"]) | 
							   Q(user=request.data["otheruser_id"], otheruser=request.data["user_id"]))
		for chatContact in chatContacts:
                                chatContacts.delete()

                return Response({"success": 20})
            else:
                return Response({"error": 17})


