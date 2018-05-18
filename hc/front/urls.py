from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from hc.front import views

check_urls = [
    url(r'^name/$', views.update_name, name="hc-update-name"),
    url(r'^timeout/$', views.update_timeout, name="hc-update-timeout"),
    url(r'^pause/$', views.pause, name="hc-pause"),
    url(r'^remove/$', views.remove_check, name="hc-remove-check"),
    url(r'^log/$', views.log, name="hc-log"),
]

channel_urls = [
    url(r'^$', views.channels, name="hc-channels"),
    url(r'^add/$', views.add_channel, name="hc-add-channel"),
    url(r'^add_email/$', views.add_email, name="hc-add-email"),
    url(r'^add_webhook/$', views.add_webhook, name="hc-add-webhook"),
    url(r'^add_pd/$', views.add_pd, name="hc-add-pd"),
    url(r'^add_slack/$', views.add_slack, name="hc-add-slack"),
    url(r'^add_slack_btn/$', views.add_slack_btn, name="hc-add-slack-btn"),
    url(r'^add_hipchat/$', views.add_hipchat, name="hc-add-hipchat"),
    url(r'^add_pushbullet/$', views.add_pushbullet, name="hc-add-pushbullet"),
    url(r'^add_pushover/$', views.add_pushover, name="hc-add-pushover"),
    url(r'^add_victorops/$', views.add_victorops, name="hc-add-victorops"),
    url(r'^([\w-]+)/checks/$', views.channel_checks, name="hc-channel-checks"),
    url(r'^([\w-]+)/remove/$', views.remove_channel, name="hc-remove-channel"),
    url(r'^([\w-]+)/verify/([\w-]+)/$', views.verify_email,
        name="hc-verify-email"),
    url(r'^add_sms/$', views.add_sms, name="hc-add-sms"),
]

urlpatterns = [
    url(r'^$', views.index, name="hc-index"),
    url(r'^checks/$', views.my_checks, name="hc-checks"),
    url(r'^checks/failed/$', views.my_failed_checks, name="hc-failed-checks"),
    url(r'^checks/add/$', views.add_check, name="hc-add-check"),
    url(r'^checks/([\w-]+)/', include(check_urls)),
    url(r'^integrations/', include(channel_urls)),
    url(r'^docs/$', views.docs, name="hc-docs"),
    url(r'^docs/api/$', views.docs_api, name="hc-docs-api"),
    url(r'^about/$', views.about, name="hc-about"),
    url(r'^task/$', views.email_task, name="hc-task"),
    url(r'^blogs/$', views.blog, name="hc-blogs"),
    url(r'^blogs/(?P<slug>[-\w.]+)$', views.view_blog_post, name="view_blog_post"),
    url(r'^blogs/add/$', views.add_blog, name="hc-add-blog"),
    url(r'^blogs/category/$', views.add_category, name="hc-add-category"),
    url(r'^blogs/comment/(?P<blogid>\d+)$', views.add_comment, name="hc-add-comment"),
    url(r'^privacy/$', views.privacy, name="hc-privacy"),
    url(r'^terms/$', views.terms, name="hc-terms"),
    url(r'^faq/$', views.faq, name="hc-faq"),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^departments/$', views.departments, name="hc-departments"),
    url(r'^departments/add/$', views.add_department, name="hc-add-department"),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)