from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from users.models import UserNotification

from reach.settings import APNS_CERF_PATH, APNS_CERF_SANDBOX_MODE

from apns import APNs, Payload


def sign_in(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        error = None
        if request.method == "POST":
            if User.objects.filter(username=request.POST["username"]).exists():
                user = get_object_or_404(User, username=request.POST["username"])
                if user.check_password(request.POST["password"]):
                    auth_user = authenticate(username=request.POST["username"],
                                             password=request.POST["password"])
                    login(request, auth_user)
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    error = "Incorrect password!"
            else:
                error = "User with that username doesn't exist!"
        return render(request, 'sign_in.html', {"error": error})


@login_required(login_url='/')
def dashboard(request):
    if request.method == "POST":
        message = request.POST["title"]
        custom = {
            "message": request.POST["text"]
        }
        apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
        payload = Payload(alert=message, sound="default", category="TEST", badge=1, custom=custom)
        notification_ids = UserNotification.objects.all().values_list("device_token", flat=True)
        for notification_id in notification_ids:
            try:
                apns.gateway_server.send_notification(notification_id, payload)
            except:
                pass
    return render(request, 'send_push.html')


@login_required(login_url='/')
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('sign_in'))
