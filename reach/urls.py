from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin

from circles.views import create_new_circle, get_all_circles, get_created_circles, get_joined_circles, get_circle, \
    join_circle, create_new_topic, get_topic, get_groups, send_reply, get_all_circles_search, \
    get_created_circles_search, get_joined_circles_search, group_circle, group_notification
from dashboard.views import sign_in, broadcast_notification, logout_user, broadcast_email
from locate.views import create_group
from posts.views import add_new_post, add_new_comment, get_user_posts, send_like, remove_like, rate_comment, \
    mark_best_response, explore_popular, explore_daily_upvotes, explore_most_upvoted, search_by_hashtag, \
    explore_popular_search, explore_daily_upvotes_search, explore_most_upvoted_search, get_single_post, remove_post, \
    get_user_new_posts, get_my_post
from users.views import registration, login, forgot_password, get_user_by_id, status_code, get_user_by_token, \
    change_email, change_password, change_bio, get_user_profile_by_token, get_user_profile_by_id, rate_user, \
    change_avatar, report_user, check_report_user_by_token, get_reported_users, send_report_email, \
    remove_reported_user, get_user_feed, send_direct_request, allow_direct_request, check_direct_request, start_call, \
    send_message, check_report_user_by_id, connect_facebook, connect_twitter, connect_instagram, read_user_feed, \
    count_unread_user_feed, update_locate, get_user_nearby, get_user_by_name, search_user_by_name, contact_request, \
    get_contact_request, delete_contact_request, accept_contact_request, get_contacts, uget_user_by_token, \
    get_password_by_ID, \
    send_notification, task_notification, delete_chat_notification, get_notification_badge, delete_notifications, \
    client_token, create_purchase, get_contact_accept_notification, unfriend_task

admin.site.site_header = 'Reach Admin'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # docs
    url(r'^api/v1/docs/status-code/$', status_code),
    # registration and login system
    url(r'^api/v1/registration/$', registration),
    url(r'^api/v1/login/$', login),
    url(r'^api/v1/forgot-password/$', forgot_password),
    # locate section
    url(r'^api/v1/locate/create-new-group/$', create_group),
    # get user(s)
    url(r'^api/v1/user/get-user-by-id/$', get_user_by_id),
    url(r'^api/v1/user/get-user-by-token/$', get_user_by_token),
    url(r'^api/v1/user/get-user-profile-by-id/$', get_user_profile_by_id),
    url(r'^api/v1/user/get-user-profile-by-token/$', get_user_profile_by_token),
    url(r'^api/v1/user/get-user-nearby/$', get_user_nearby),
    url(r'^api/v1/user/get-user-by-name/$', get_user_by_name),
    url(r'^api/v1/user/search-user-by-name/$', search_user_by_name),
    url(r'^api/v1/user/uget-user-by-token/$', uget_user_by_token),
    url(r'^api/v1/user/get-password-by-id/$', get_password_by_ID),
    url(r'^api/v1/user/send-notification/$', send_notification),
    url(r'^api/v1/user/task-notification/$', task_notification),
    url(r'^api/v1/user/read-chat-notification/$', delete_chat_notification),
    url(r'^api/v1/user/get-notification-badge/$', get_notification_badge),
    url(r'^api/v1/user/delete-notification-badge/$', delete_notifications),
    url(r'^api/v1/user/bt-client-token/$', client_token),
    url(r'^api/v1/user/bt-create-purchase/$', create_purchase),
    url(r'^api/v1/user/get-contact-accept-notification/$', get_contact_accept_notification),
    url(r'^api/v1/user/unfriend-task/$', unfriend_task),
    # chats
    url(r'^api/v1/user/contact-request/$', contact_request),
    url(r'^api/v1/user/get-contact-request/$', get_contact_request),
    url(r'^api/v1/user/delete-contact-request/$', delete_contact_request),
    url(r'^api/v1/user/accept-contact-request/$', accept_contact_request),
    url(r'^api/v1/user/get-contacts/$', get_contacts),
    # report user
    url(r'^api/v1/user/report-user/$', report_user),
    url(r'^api/v1/user/remove-reported-user/$', remove_reported_user),
    url(r'^api/v1/user/check-report-user-by-token/$', check_report_user_by_token),
    url(r'^api/v1/user/check-report-user-by-id/$', check_report_user_by_id),
    url(r'^api/v1/user/get-reported-users/$', get_reported_users),
    url(r'^api/v1/user/send-report-email/$', send_report_email),
    # edit user
    url(r'^api/v1/user/change-email/$', change_email),
    url(r'^api/v1/user/change-password/$', change_password),
    url(r'^api/v1/user/change-avatar/$', change_avatar),
    url(r'^api/v1/user/change-bio/$', change_bio),
    url(r'^api/v1/user/update-locate/$', update_locate),
    url(r'^api/v1/user/social/facebook/$', connect_facebook),
    url(r'^api/v1/user/social/twitter/$', connect_twitter),
    url(r'^api/v1/user/social/instagram/$', connect_instagram),
    # posts
    url(r'^api/v1/post/add-new-post/$', add_new_post),
    url(r'^api/v1/post/remove-post/$', remove_post),
    url(r'^api/v1/post/get-user-posts/$', get_user_posts),
    url(r'^api/v1/post/get-user-new-posts/$', get_user_new_posts),
    url(r'^api/v1/post/get-single-post/$', get_single_post),
    url(r'^api/v1/post/get-my-post/$', get_my_post),
    # comments to posts
    url(r'^api/v1/post/add-new-comment/$', add_new_comment),
    url(r'^api/v1/post/rate-comment/$', rate_comment),
    url(r'^api/v1/post/mark-best-response/$', mark_best_response),
    # likes to posts
    url(r'^api/v1/post/send-like/$', send_like),
    url(r'^api/v1/post/remove-like/$', remove_like),
    # circles
    url(r'^api/v1/circle/create-new-circle/$', create_new_circle),
    url(r'^api/v1/circle/get-all-circles/$', get_all_circles),
    url(r'^api/v1/circle/get-created-circles/$', get_created_circles),
    url(r'^api/v1/circle/get-joined-circles/$', get_joined_circles),
    url(r'^api/v1/circle/get-circle/$', get_circle),
    url(r'^api/v1/circle/join-circle/$', join_circle),
    url(r'^api/v1/circle/get-circle-by-group/$', group_circle),
    url(r'^api/v1/circle/get-circle-notification/$', group_notification),
    # topics
    url(r'^api/v1/topic/create-new-topic/$', create_new_topic),
    url(r'^api/v1/topic/get-topic/$', get_topic),
    # reply to topics
    url(r'^api/v1/reply/send-reply/$', send_reply),
    # groups
    url(r'^api/v1/groups/get-groups/$', get_groups),
    # explore
    url(r'^api/v1/explore/get-popular/$', explore_popular),
    url(r'^api/v1/explore/get-daily-upvotes/$', explore_daily_upvotes),
    url(r'^api/v1/explore/get-most-upvoted/$', explore_most_upvoted),
    # search hashtag
    url(r'^api/v1/search/hashtag/$', search_by_hashtag),
    # search explore
    url(r'^api/v1/explore/get-popular/search/$', explore_popular_search),
    url(r'^api/v1/explore/get-daily-upvotes/search/$', explore_daily_upvotes_search),
    url(r'^api/v1/explore/get-most-upvoted/search/$', explore_most_upvoted_search),
    # search circles
    url(r'^api/v1/circle/get-all-circles/search/$', get_all_circles_search),
    url(r'^api/v1/circle/get-created-circles/search/$', get_created_circles_search),
    url(r'^api/v1/circle/get-joined-circles/search/$', get_joined_circles_search),
    # rate
    url(r'^api/v1/rate/rate-user/$', rate_user),
    # feed
    url(r'^api/v1/feed/get-user-feed/$', get_user_feed),
    url(r'^api/v1/feed/read-feed/$', read_user_feed),
    url(r'^api/v1/feed/count-unread-feed/$', count_unread_user_feed),
    # direct messaging/VOIP access
    url(r'^api/v1/direct/send-request/$', send_direct_request),
    url(r'^api/v1/direct/allow-request/$', allow_direct_request),
    url(r'^api/v1/direct/check-request-status/$', check_direct_request),
    url(r'^api/v1/message/send-message/$', send_message),
    # VOIP push
    url(r'^api/v1/voip/start-call/$', start_call),

    # Dashboard WEB view
    # login/logout system
    url(r'^$', sign_in, name="sign_in"),
    url(r'^logout/$', logout_user, name="logout_user"),
    # main page with profile info
    url(r'^broadcast_notification/', broadcast_notification, name="broadcast_notification"),
    url(r'^broadcast_email/', broadcast_email, name="broadcast_email"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
