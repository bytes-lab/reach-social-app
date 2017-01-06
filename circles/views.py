from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Q
from django.contrib.auth.models import User

from users.models import UserFeed, UserNotification, UserReport
from circles.models import Circle, UserCircle, Topic, Group, TopicComment, Notification
from circles.serializers import CircleSerializer, TopicSerializer, GroupSerializer, FullCircleSerializer, NotificationSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from base64 import b64decode

from reach.settings import PAGE_OFFSET
from utils import send_notification


@api_view(["POST"])
def create_new_circle(request):
    """
Create a new circle.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "name": "Anger",
        "description": "Let's talk about anger",
        "image": "base64 string goes here",
        "group_id": 1,
        "permission": true
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circle": {
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
                    "biography": "",
                    "like_count": 0,
                    "comment_count": 0,
                    "rate": 0,
                    "avatar": "/media/default_images/default.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                }
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
            "join": true,
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
                            },
                            "text": "my aweasome text",
                            "permission": true,
                            "date": "2016-02-03T14:52:34.359412Z"
                        }
                    ]
                }
            ]
        },
        "success": 47
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if "name" in request.data and request.data["name"] != "" and request.data["name"] is not None:
                    if len(request.data["name"]) < 3:
                        return Response({"error": 42})
                    elif len(request.data["name"]) > 50:
                        return Response({"error": 43})
                    else:
                        if Circle.objects.filter(name=request.data["name"]).exists():
                            return Response({"error": 46})
                        else:
                            if "description" in request.data and request.data["description"] != "" and \
                                    request.data["description"] is not None:
                                if len(request.data["description"]) < 3:
                                    return Response({"error": 44})
                                elif len(request.data["description"]) > 500:
                                    return Response({"error": 45})
                                else:
                                    if Group.objects.filter(pk=request.data["group_id"]).exists():
                                        token = get_object_or_404(Token, key=request.data["token"])
                                        circle = Circle.objects.create(owner_id=token.user_id,
                                                                       name=request.data["name"],
                                                                       description=request.data["description"],
                                                                       group_id=request.data["group_id"],
                                                                       permission=request.data["permission"])
                                        if "image" in request.data and request.data["image"] != "" \
                                                and request.data["image"] is not None:
                                            image_data = b64decode(request.data["image"])
                                            circle.image = ContentFile(image_data, "circle.png")
                                            circle.save()
                                        # UserCircle.objects.create(circle=circle, user_id=token.user_id)
                                        serializer = CircleSerializer(circle, context={'user_id': token.user_id})
                                        return Response({"success": 47,
                                                         "circle": serializer.data})
                                    else:
                                        return Response({"error": 59})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def circle_search(request):
    """
    Get all available circles.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "group_id": 23,
            "circle_id": 54,
            "type": "new" or "old",
            "keyword": "happy"
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                    "join": true
                }
            ],
            "success": 48,
            "offset": 10
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    token = request.data.get('token')
    group_id = request.data.get('group_id')
    circle_id = request.data.get('circle_id')
    type_ = request.data.get('type')
    keyword = request.data.get('keyword')

    if Token.objects.filter(key=request.data["token"]).exists():
        token = get_object_or_404(Token, key=token)
        circles = Circle.objects.all()
        if group_id > 0:
            circles = circles.filter(group_id=group_id)
        circles = circles.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))

        if circle_id == -1:
            circles = circles.order_by("-date")[:PAGE_OFFSET]
        elif type_ == 'old':
            circles = circles.filter(pk__lt=circle_id).order_by("-date")[:PAGE_OFFSET]
        else: # 'new'
            circles = reversed(circles.filter(pk__gt=circle_id).order_by("date")[:PAGE_OFFSET])

        # serializer = CircleSerializer(circles, context={'user_id': token.user_id}, many=True)
        serializer = FullCircleSerializer(circles, context={'user_id': token.user_id}, many=True)
        
        return Response({"success": 48,
                         "circles": serializer.data})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def get_all_circles_search(request):
    """
    Search all available circles.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "keyword": "qwerty",
            "offset": 0
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                    "join": true
                }
            ],
            "success": 48
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                start_offset = request.data["offset"]
                end_offset = start_offset + PAGE_OFFSET
                circles = Circle.objects.filter(Q(name__contains=request.data["keyword"]) |
                                                Q(description=request.data["keyword"]))[start_offset:end_offset]
                token = get_object_or_404(Token, key=request.data["token"])
                serializer = CircleSerializer(circles, context={'user_id': token.user_id}, many=True)
                return Response({"success": 48,
                                 "circles": serializer.data,
                                 "offset": end_offset})
            else:
                return Response({"error": 17})

@api_view(["POST"])
def get_created_circles(request):
    """
Get all available created circles.

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
                        "biography": "",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 0,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    }
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
                "join": true
            }
        ],
        "success": 49,
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
                end_offset = start_offset + PAGE_OFFSET
                circles = Circle.objects.filter(owner_id=token.user_id)[start_offset:end_offset]
                serializer = FullCircleSerializer(circles, context={'user_id': token.user_id}, many=True)
                return Response({"success": 49,
                                 "circles": serializer.data,
                                 "offset": end_offset})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_joined_circles(request):
    """
    Get all available joined circles.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "circle_id": 54,
            "type": "new" or "old",
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                    "join": true
                }
            ],
            "success": 50,
            "offset": 10
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    token = request.data.get('token')
    circle_id = request.data.get('circle_id')
    type_ = request.data.get('type')

    if Token.objects.filter(key=token).exists():
        token = get_object_or_404(Token, key=token)
        user_circles = UserCircle.objects.filter(user_id=token.user_id).values_list("circle_id", flat=True)
        # reported_users = UserReport.objects.filter(user=token.user).values_list('reported_id', flat=True)
        # circles = Circle.objects.exclude(owner__in=reported_users).filter(pk__in=user_circles)[start_offset:end_offset]
        circles = Circle.objects.filter(pk__in=user_circles)
        if circle_id == -1:
            circles = circles.order_by("-date")[:PAGE_OFFSET]
        elif type_ == 'old':
            circles = circles.filter(pk__lt=circle_id).order_by("-date")[:PAGE_OFFSET]
        else: # 'new'
            circles = reversed(circles.filter(pk__gt=circle_id).order_by("date")[:PAGE_OFFSET])
        
        serializer = FullCircleSerializer(circles, context={'user_id': token.user_id}, many=True)
        return Response({"success": 50,
                         "circles": serializer.data})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def get_circle(request):
    """
Get single circle by circle_id.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "circle_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circle": {
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
                    "biography": "",
                    "like_count": 0,
                    "comment_count": 0,
                    "rate": 0,
                    "avatar": "/media/default_images/default.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                }
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
                            },
                            "text": "my aweasome text",
                            "permission": true,
                            "date": "2016-02-03T14:52:34.359412Z"
                        }
                    ]
                }
            ]
        },
        "success": 52
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if Circle.objects.filter(pk=request.data["circle_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    circle = get_object_or_404(Circle, pk=request.data["circle_id"])
                    serializer = FullCircleSerializer(circle, context={'user_id': token.user_id})
                    return Response({"success": 52,
                                     "circle": serializer.data})
                else:
                    return Response({"error": 51})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def join_circle(request):
    """
    Join/Unjoin circle via circle_id.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "circle_id": 1
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "circle": {
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
                        "biography": "",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 0,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    }
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
                                "biography": "",
                                "like_count": 0,
                                "comment_count": 0,
                                "rate": 0,
                                "avatar": "/media/default_images/default.png",
                                "is_facebook": false,
                                "is_twitter": false,
                                "is_instagram": false
                            }
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
                                        "biography": "",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    }
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
                                        "biography": "",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    }
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
                                        "biography": "",
                                        "like_count": 0,
                                        "comment_count": 0,
                                        "rate": 0,
                                        "avatar": "/media/default_images/default.png",
                                        "is_facebook": false,
                                        "is_twitter": false,
                                        "is_instagram": false
                                    }
                                },
                                "text": "my aweasome text",
                                "permission": true,
                                "date": "2016-02-03T14:52:34.359412Z"
                            }
                        ]
                    }
                ]
            },
            "success": 54
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if Circle.objects.filter(pk=request.data["circle_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    circle = get_object_or_404(Circle, pk=request.data["circle_id"])
                    if UserCircle.objects.filter(circle=circle, user_id=token.user_id).exists():
                        UserCircle.objects.filter(circle=circle, user_id=token.user_id).delete()
                    else:
                        UserCircle.objects.create(circle=circle, user_id=token.user_id)
                        Notification.objects.create(user=circle.owner,
                                                    circle=circle,
                                                    otheruser_id=token.user_id,
                                                    detail="Join your Group",
                                                    notitype=2)

                        custom = {
                            "circle_id": circle.id
                        }
                        message = "{} joined into your circle".format(token.user.username)
                        user_notification = UserNotification.objects.get(user=circle.owner)
                        send_notification(custom, message, user_notification)

                    # serializer = CircleSerializer(circle, context={'user_id': token.user_id})
                    serializer = FullCircleSerializer(circle, context={'user_id': token.user_id})
                    
                    return Response({"success": 54,
                                     "circle": serializer.data})
                else:
                    return Response({"error": 51})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def create_new_topic(request):
    """
Create new topic in circle.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "circle_id": 1,
        "text": "some problem here",
        "permission": true
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circle": {
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
                    "biography": "",
                    "like_count": 0,
                    "comment_count": 0,
                    "rate": 0,
                    "avatar": "/media/default_images/default.png",
                    "is_facebook": false,
                    "is_twitter": false,
                    "is_instagram": false
                }
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
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
                                    "biography": "",
                                    "like_count": 0,
                                    "comment_count": 0,
                                    "rate": 0,
                                    "avatar": "/media/default_images/default.png",
                                    "is_facebook": false,
                                    "is_twitter": false,
                                    "is_instagram": false
                                }
                            },
                            "text": "my aweasome text",
                            "permission": true,
                            "date": "2016-02-03T14:52:34.359412Z"
                        }
                    ]
                }
            ]
        },
        "success": 54
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if Circle.objects.filter(pk=request.data["circle_id"]).exists():
                    token = get_object_or_404(Token, key=request.data["token"])
                    circle = get_object_or_404(Circle, pk=request.data["circle_id"])
                    if UserCircle.objects.filter(circle=circle, user_id=token.user_id).exists():
                        topic = Topic.objects.create(author_id=token.user_id,
                                             circle=circle,
                                             text=request.data["text"],
                                             permission=request.data["permission"])

                        Notification.objects.create(user=circle.owner, 
                                                    circle=circle,
                                                    otheruser_id=token.user_id,
                                                    detail=request.data["text"],
                                                    notitype=1,
                                                    topic=topic)

                        custom = {
                            "circle_id": circle.id
                        }
                        message = "{} created a new topic in your circle".format(token.user.username)
                        user_notification = UserNotification.objects.get(user=circle.owner)
                        send_notification(custom, message, user_notification)

                        # send notifications to topic owners in the circle
                        for user in [item.user for item in UserCircle.objects.filter(circle=circle)]:
                            if user != token.user:
                                Notification.objects.create(user=user, 
                                                            circle=circle,
                                                            otheruser_id=token.user_id,
                                                            detail=request.data["text"],
                                                            notitype=1,
                                                            topic=topic)

                                message = "{} created a new topic in your circle".format(user.username)
                                user_notification = UserNotification.objects.get(user=user)
                                send_notification(custom, message, user_notification)

                        serializer = FullCircleSerializer(circle, context={'user_id': token.user_id})
                        return Response({"success": 55,
                                         "circle": serializer.data})
                    else:
                        return Response({"error": 53})
                else:
                    return Response({"error": 51})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_topic(request):
    """
Get single topic in circle.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "topic_id": 1
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "topic": {
            "id": 1,
            "author": {
                "id": 2,
                "username": "antonboksha",
                "first_name": "",
                "last_name": "",
                "email": "antonboksha@gmail.com",
                "info": {
                    "full_name": "",
                    "biography": "",
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
            "date": "2016-02-02T14:16:59.161082Z"
        },
        "success": 56
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    if request.method == "POST":
        if "token" in request.data and request.data["token"] != "" and request.data["token"] is not None:
            if Token.objects.filter(key=request.data["token"]).exists():
                if Topic.objects.filter(pk=request.data["topic_id"]).exists():
                    topic = get_object_or_404(Topic, pk=request.data["topic_id"])
                    serializer = TopicSerializer(topic)
                    return Response({"success": 56,
                                     "topic": serializer.data})
                else:
                    return Response({"error": 57})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_groups(request):
    """
    Get list of groups and count of circles in each group.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "keyword": "holiday"
        }

        Code statuses can be found here: /api/v1/docs/status-code/

        Success json:
        {
            "groups": [
                {
                    "id": 1,
                    "name": "sex",
                    "count_circles": 1
                },
                {
                    "id": 2,
                    "name": "anger",
                    "count_circles": 0
                }
            ],
            "success": 58
        }

        Fail json:
        {
            "error": <status_code>
        }
    """
    token = request.data.get('token')
    keyword = request.data.get('keyword', '')    
    if Token.objects.filter(key=token).exists():
        groups = Group.objects.filter(name__icontains=keyword).order_by("name")
        serializer = GroupSerializer(groups, many=True)
        return Response({"success": 58,
                         "groups": serializer.data})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def send_reply(request):
    """
Send reply to the topic in circle.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "topic_id": 1,
        "permission": true,
        "text": "my aweasome text"
    }

    Code statuses can be found here: /api/v1/docs/status-code/

    Success json:
    {
        "circle": {
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
                    "biography": "",
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
                            "biography": "",
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
                                    "biography": "",
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
                                    "biography": "",
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
                                    "biography": "",
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
        },
        "success": 58
    }

    Fail json:
    {
        "error": <status_code>
    }
    """
    token = request.data.get('token')
    if Token.objects.filter(key=token).exists():
        if Topic.objects.filter(pk=request.data["topic_id"]).exists():
            token = get_object_or_404(Token, key=request.data["token"])
            topic = get_object_or_404(Topic, pk=request.data["topic_id"])
            topic_comment = TopicComment.objects.create(topic=topic,
                                                        author_id=token.user_id,
                                                        text=request.data["text"],
                                                        permission=request.data["permission"])
            circle = get_object_or_404(Circle, pk=topic.circle_id)
            serializer = FullCircleSerializer(circle)
            text = request.data.get('text')

            Notification.objects.create(user=circle.owner,
                                        circle=topic.circle,
                                        otheruser_id=token.user_id,
                                        notitype=0,
                                        topic=topic,
                                        detail=request.data["text"])

            Notification.objects.create(user=topic.author,
                                        circle=topic.circle,
                                        otheruser_id=token.user_id,
                                        notitype=0,
                                        topic=topic,
                                        detail=request.data["text"])
					       
            # if request.data["permission"]:
                # UserFeed.objects.create(user=topic.author,
                #                         action_user=token.user,
                #                         action="TopicComment",
                #                         topic_comment=topic_comment)
            custom = {
                "circle_id": circle.id
            }

            message = "{} comment your topic".format(token.user.username)

            if topic.author != token.user:
                user_notification = UserNotification.objects.get(user=topic.author)
                send_notification(custom, message, user_notification)

            # check @ for users                    
            for item in text.split(' '):
                if item and item[0] == '@':
                    username = item[1:].lower()
                    user = User.objects.filter(username__iexact=username).first()
                    if not user:
                        continue
                    Notification.objects.create(user=user,
                                                circle=topic.circle,
                                                otheruser_id=token.user_id,
                                                notitype=0,
                                                topic=topic,
                                                detail=request.data["text"])

                    # UserFeed.objects.create(user=user,
                    #                         action_user=token.user,
                    #                         topic_comment=comment,
                    #                         action="TopicCommentComment")
                    message = "{} commented on your comment".format(token.user.username)

                    if user != token.user:
                        user_notification = UserNotification.objects.get(user=user)
                        send_notification(custom, message, user_notification)

            return Response({"success": 58,
                             "circle": serializer.data})
        else:
            return Response({"error": 57})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def get_created_circles_search(request):
    """
    Search all available created circles.

        Example json:
        {
            "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
            "keyword": "qwerty",
            "offset": 0
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
                            "biography": "",
                            "like_count": 0,
                            "comment_count": 0,
                            "rate": 0,
                            "avatar": "/media/default_images/default.png",
                            "is_facebook": false,
                            "is_twitter": false,
                            "is_instagram": false
                        }
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
                    "join": true
                }
            ],
            "success": 49
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
                end_offset = start_offset + PAGE_OFFSET
                reported_users = UserReport.objects.filter(user=token.user).values_list('reported_id', flat=True)
                circles = Circle.objects.exclude(owner__in=reported_users).filter(owner_id=token.user_id).filter(
                    Q(name__icontains=request.data["keyword"]) |
                    Q(description__icontains=request.data["keyword"]))[start_offset:end_offset]
                serializer = CircleSerializer(circles, context={'user_id': token.user_id}, many=True)
                return Response({"success": 49,
                                 "circles": serializer.data,
                                 "offset": end_offset})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def get_joined_circles_search(request):
    """
Get all available joined circles.

    Example json:
    {
        "token": "9bb7176dcdd06d196ef38c17600840d13943b9df",
        "offset": 0
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
                        "biography": "",
                        "like_count": 0,
                        "comment_count": 0,
                        "rate": 0,
                        "avatar": "/media/default_images/default.png",
                        "is_facebook": false,
                        "is_twitter": false,
                        "is_instagram": false
                    }
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
                "join": true
            }
        ],
        "success": 50
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
                user_circles = UserCircle.objects.filter(user_id=token.user_id).values_list("circle_id", flat=True)
                start_offset = request.data["offset"]
                end_offset = start_offset + PAGE_OFFSET
                reported_users = UserReport.objects.filter(user=token.user).values_list('reported_id', flat=True)
                circles = Circle.objects.exclude(owner__in=reported_users).filter(pk__in=user_circles).filter(
                    Q(name__contains=request.data["keyword"]) |
                    Q(description=request.data["keyword"]))[start_offset:end_offset]
                serializer = CircleSerializer(circles, context={'user_id': token.user_id}, many=True)
                return Response({"success": 50,
                                 "circles": serializer.data,
                                 "offset": end_offset})
            else:
                return Response({"error": 17})


@api_view(["POST"])
def group_notification(request):
    """
    Get read/unread circle notifications.

        Example json:
        {
            "token": "",
            "notification_id": 37,
            "type": "new" or "old"
        }

    """
    token = request.data.get('token')
    notification_id = request.data.get('notification_id')
    type_ = request.data.get('type')

    if Token.objects.filter(key=token).exists():
        token = get_object_or_404(Token, key=token)
        if type_ == 'old':
            if notification_id == -1:
                notification = Notification.objects.filter(user=token.user, read=True) \
                                       .exclude(otheruser=token.user) \
                                       .order_by("-date")
            else:
                notification = Notification.objects.filter(user=token.user, pk__lt=notification_id, read=True) \
                                       .exclude(otheruser=token.user) \
                                       .order_by("-date")
        else: # 'new'
            notification = Notification.objects.filter(user=token.user, read=False) \
                                   .exclude(otheruser=token.user) \
                                   .order_by("-date")

        serializer = NotificationSerializer(notification, many=True)
        return Response({"success": 48,
                         "notifications": serializer.data})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def read_group_notification(request):
    token = request.data.get('token')
    notification_id = request.data.get('notification_id')
    if Token.objects.filter(key=token).exists():
        token = get_object_or_404(Token, key=token)
        Notification.objects.filter(user=token.user, pk__lte=notification_id, read=False) \
                        .update(read=True)
        return Response({"success": 89})
    else:
        return Response({"error": 17})


@api_view(["POST"])
def unread_group_notifications(request):
    if Token.objects.filter(key=request.data["token"]).exists():
        token = get_object_or_404(Token, key=request.data["token"])
        unread_count = Notification.objects.filter(user=token.user,
                                                   read=False) \
                                           .exclude(otheruser=token.user) \
                                           .count()
        return Response({"success": 90,
                         "unread_count": unread_count})
    else:
        return Response({"error": 17})
