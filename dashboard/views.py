from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from users.models import UserNotification
from reach.settings import APNS_CERF_PATH, APNS_CERF_SANDBOX_MODE, BASE_DIR
from apns import APNs, Payload


def sign_in(request):
    return HttpResponseRedirect('/admin/')
    
    if request.user.is_authenticated():
        return HttpResponseRedirect('/admin/')
    else:
        error = None
        if request.method == "POST":
            if User.objects.filter(username=request.POST["username"]).exists():
                user = get_object_or_404(User, username=request.POST["username"])
                if user.check_password(request.POST["password"]):
                    auth_user = authenticate(username=request.POST["username"],
                                             password=request.POST["password"])
                    login(request, auth_user)
                    return HttpResponseRedirect(reverse('sign_in'))
                else:
                    error = "Incorrect password!"
            else:
                error = "User with that username doesn't exist!"
        return render(request, 'sign_in.html', {"error": error})


@login_required(login_url='/')
def broadcast_notification(request):
    user_ids = request.GET.get('ids').split(',')

    if request.method == "POST":
        message = request.POST["title"]
        custom = {
            "message": request.POST["text"]
        }

        apns = APNs(use_sandbox=APNS_CERF_SANDBOX_MODE, cert_file=APNS_CERF_PATH)
        payload = Payload(alert=message, sound="default", 
            category="TEST", badge=1, custom=custom)

        for nf in UserNotification.objects.filter(user_id__in=user_ids):
            try:
                device_token = nf.device_token.replace('-', '')
                apns.gateway_server.send_notification(device_token, payload)
            except:
                print device_token, '######'
                raise

    return render(request, 'send_push.html')


@login_required(login_url='/')
def broadcast_email(request):
    user_ids = request.GET.get('ids').split(',')

    if request.method == "POST":
        subject = request.POST["subject"]
        content = request.POST["content"]

        for user in User.objects.filter(id__in=user_ids):
            user.email_user(subject, content)

        return HttpResponseRedirect('/admin/auth/user')
    return render(request, 'broadcast_email.html')


@login_required(login_url='/')
def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('sign_in'))
