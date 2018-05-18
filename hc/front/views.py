from collections import Counter
from datetime import timedelta as td
from itertools import tee

import requests
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.six.moves.urllib.parse import urlencode
from hc.api.decorators import uuid_or_400
from hc.front.models import Category, Blog, Comment, EmailTasks
from hc.api.models import DEFAULT_GRACE, DEFAULT_TIMEOUT, Department, Channel, Check, Ping, PO_PRIORITIES, AssignedChecks, NO_PRIORITY
from hc.front.forms import (AddChannelForm, AddDepartmentForm, AddWebhookForm, NameTagsForm,
                            TimeoutForm, AddBlogForm, AddCategoryForm, AddCommentForm,
                            FaqForm, EmailTaskForm)

from hc.front.models import FrequentlyAskedQuestion

# from itertools recipes:
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


@login_required
def my_checks(request):
    if request.user.id == request.team.user.id:
        check_rows = Check.objects.filter(user=request.team.user)
    else:
        check_rows = []
        assigned_checkrows = AssignedChecks.objects.filter(team=request.team.user.profile, user=request.user)
        for assigned_checkrow in assigned_checkrows:
            check_rows.append(assigned_checkrow.checks)

    recieved_checks = list(check_rows)
    checks = []

    for x in range(-2, 3):
        for check in recieved_checks:
            if check.priority == PO_PRIORITIES[x]:
                checks.append(check)
    checks.reverse()

    if request.GET.get('department') and request.GET.get('department') != "all":
        try:
            department = int(request.GET.get('department'))
        except ValueError:
            raise Http404("Department specified cannot be found.")
    else:
        department = "all"
    if department != "all":
        checks = [check for check in checks if check.department_id == department]
    depts = Department.objects.filter(user=request.team.user)

    counter = Counter()
    down_tags, grace_tags = set(), set()
    for check in checks:
        status = check.get_status()
        for tag in check.tags_list():
            if tag == "":
                continue

            counter[tag] += 1

            if status == "down":
                down_tags.add(tag)
            elif check.in_grace_period():
                grace_tags.add(tag)

    ctx = {
        "page": "checks",
        "page_title": 'My Checks',
        "checks": checks,
        "departments": depts,
        "department": department,
        "now": timezone.now(),
        "tags": counter.most_common(),
        "down_tags": down_tags,
        "grace_tags": grace_tags,
        "ping_endpoint": settings.PING_ENDPOINT
    }
    return render(request, "front/my_checks.html", ctx)

@login_required
def my_failed_checks(request):

    """ Views function for retieving and displaying all failed checks """

    if request.user.id == request.team.user.id:
        check_rows = Check.objects.filter(user=request.team.user).order_by("created")
    else:
        check_rows = []
        assigned_checkrows = AssignedChecks.objects.filter(team=request.team.user.profile, user=request.user).order_by("created")
        for assigned_checkrow in assigned_checkrows:
            check_rows.append(assigned_checkrow.checks)

    checks = list(check_rows)
    
    failed_checks = []
    for check in checks:
        if check.get_status() == "down":
            failed_checks.append(check)


    ctx = {
        "page": "failed_checks",
        "page_title": 'My Failed Checks',
        "checks": failed_checks,
        "now": timezone.now(),
        "ping_endpoint": settings.PING_ENDPOINT
    }

    return render(request, "front/my_checks.html", ctx)

@login_required
def assign_checks(request, email):
    team = request.user.profile
    user = User.objects.get(email=email)
    for key in request.POST:
        if key.startswith("check-"):
            code = key[6:]
            try:
                check = Check.objects.get(code=code)
            except Check.DoesNotExist:
                return HttpResponseBadRequest()
            if check.user_id != request.team.user.id:
                return HttpResponseForbidden()
            assigned_check = AssignedChecks(user = user, team = team, checks = check)
            assigned_check.save()

@login_required
def assign_checks_priority(request, email):
    team = request.user.profile
    user = User.objects.get(email=email)
    for key in request.POST:
        if key.startswith("check-"):
            code = key[6:]
            priority = request.POST["notification-priority-"+code]

            try:
                check = Check.objects.get(code=code)
            except Check.DoesNotExist:
                return HttpResponseBadRequest()
            if check.user_id != request.team.user.id:
                return HttpResponseForbidden()
            assigned_check = AssignedChecks.objects.get(user=user, team=team, checks=check)
            assigned_check.notofication_priority = NO_PRIORITY[int(priority)]
            assigned_check.save()

def _welcome_check(request):
    check = None
    if "welcome_code" in request.session:
        code = request.session["welcome_code"]
        check = Check.objects.filter(code=code).first()

    if check is None:
        check = Check()
        check.save()
        request.session["welcome_code"] = str(check.code)

    return check


def index(request):
    if request.user.is_authenticated:
        return redirect("hc-checks")

    check = _welcome_check(request)

    ctx = {
        "page": "welcome",
        "check": check,
        "ping_url": check.url(),
        "enable_pushover": settings.PUSHOVER_API_TOKEN is not None
    }

    return render(request, "front/welcome.html", ctx)


def docs(request):
    check = _welcome_check(request)

    ctx = {
        "page": "docs",
        "section": "home",
        "ping_endpoint": settings.PING_ENDPOINT,
        "check": check,
        "ping_url": check.url()
    }

    return render(request, "front/docs.html", ctx)


def docs_api(request):
    ctx = {
        "page": "docs",
        "section": "api",
        "SITE_ROOT": settings.SITE_ROOT,
        "PING_ENDPOINT": settings.PING_ENDPOINT,
        "default_timeout": int(DEFAULT_TIMEOUT.total_seconds()),
        "default_grace": int(DEFAULT_GRACE.total_seconds())
    }

    return render(request, "front/docs_api.html", ctx)


def about(request):
    return render(request, "front/about.html", {"page": "about"})


def email_task(request):
    """
    allows user to schedule standard tasks
    """
    current_user = request.user
    tasks = EmailTasks.objects.all()
    if request.method == "POST":
        form = EmailTaskForm(request.POST)
        if form.is_valid():
            task_name = form.cleaned_data['task_name']
            subject = form.cleaned_data['subject']
            recipients = form.cleaned_data['recipients']
            message = form.cleaned_data['message']
            interval = form.cleaned_data['interval']
            time = form.cleaned_data['time']
            owner = current_user
            task = EmailTasks(task_name=task_name, subject=subject, recipients=recipients, message=message, interval=interval,time=time,owner=owner)
            task.save()
            messages.success(request, "Your task has been saved!")
    else:
        form = EmailTaskForm()

    return render(request, "front/scheduled_task.html", {"form": form, "tasks":tasks})


def blog(request):
    """ list all blogs """
    blogs_list = Blog.objects.all()
    category_list = Category.objects.all()

    return render(request, "front/blogs.html", {"blogs_list":blogs_list, "category_list":category_list})

def view_blog_post(request, slug):
    """ return full blog """
    blog = Blog.objects.get(slug=slug)
    comments = Comment.objects.filter(blog=blog)
    if comments:
        return render(request, "front/blog_detail.html", {"blog":blog, "comments":comments})
        
    return render(request, "front/blog_detail.html", {"blog":blog})

@login_required
def add_category(request):
    """ adding new category"""

    if request.method == "POST":
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            post = Category(title=category)
            post.save()

            return HttpResponseRedirect('/blogs/')
    else:
        form = AddCategoryForm()

    return render(request, "front/add_category.html", {'form':form})

@login_required
def add_blog(request):
    """ adding a blog """
    current_user = request.user
    if request.method == "POST":
        form = AddBlogForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            category = form.cleaned_data['category']
            body = form.cleaned_data['body']
            author = current_user
            post = Blog(title=title, category=category, body=body, author=author)
            post.save()

            return HttpResponseRedirect('/blogs/')
    else:
        form = AddBlogForm()

    return render(request, "front/add_blog.html", {'form':form})

@login_required
def add_comment(request, blogid):
    blog = get_object_or_404(Blog, pk=blogid)
    #print(blog.id)
    current_user = request.user
    if request.method == "POST":
        form = AddCommentForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            post = Comment(body=comment, blog=blog, name=current_user)
            post.save()

            return HttpResponseRedirect('/blogs/')
    else:
        form = AddCommentForm()

    return render(request, "front/add_comment.html", {'form':form})




@login_required
def add_check(request):
    assert request.method == "POST"

    check = Check(user=request.team.user)
    check.save()

    check.assign_all_channels()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def update_name(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user_id != request.team.user.id:
        return HttpResponseForbidden()

    form = NameTagsForm(request.POST)
    if form.is_valid():
        check.name = form.cleaned_data["name"]
        check.tags = form.cleaned_data["tags"]
        check.department_id = form.cleaned_data["department"]
        check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def update_timeout(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    form = TimeoutForm(request.POST)
    if form.is_valid():
        check.timeout = td(seconds=form.cleaned_data["timeout"])
        check.grace = td(seconds=form.cleaned_data["grace"])
        priority_id = int(form.cleaned_data["priority"])
        check.priority = PO_PRIORITIES[priority_id]
        check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def pause(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user_id != request.team.user.id:
        return HttpResponseForbidden()

    check.status = "paused"
    check.save()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def remove_check(request, code):
    assert request.method == "POST"

    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    check.delete()

    return redirect("hc-checks")


@login_required
@uuid_or_400
def log(request, code):
    check = get_object_or_404(Check, code=code)
    if check.user != request.team.user:
        return HttpResponseForbidden()

    limit = request.team.ping_log_limit
    pings = Ping.objects.filter(owner=check).order_by("-id")[:limit]

    pings = list(pings.iterator())
    # oldest-to-newest order will be more convenient for adding
    # "not received" placeholders:
    pings.reverse()

    # Add a dummy ping object at the end. We iterate over *pairs* of pings
    # and don't want to handle a special case of a check with a single ping.
    pings.append(Ping(created=timezone.now()))

    # Now go through pings, calculate time gaps, and decorate
    # the pings list for convenient use in template
    wrapped = []

    early = False
    for older, newer in pairwise(pings):
        wrapped.append({"ping": older, "early": early})

        # Fill in "missed ping" placeholders:
        expected_date = older.created + check.timeout
        n_blanks = 0
        while expected_date + check.grace < newer.created and n_blanks < 10:
            wrapped.append({"placeholder_date": expected_date})
            expected_date = expected_date + check.timeout
            n_blanks += 1

        # Prepare early flag for next ping to come
        early = older.created + check.timeout > newer.created + check.grace

    reached_limit = len(pings) > limit

    wrapped.reverse()
    ctx = {
        "check": check,
        "pings": wrapped,
        "num_pings": len(pings),
        "limit": limit,
        "show_limit_notice": reached_limit and settings.USE_PAYMENTS
    }

    return render(request, "front/log.html", ctx)


@login_required
def channels(request):
    if request.method == "POST":
        code = request.POST["channel"]
        try:
            channel = Channel.objects.get(code=code)
        except Channel.DoesNotExist:
            return HttpResponseBadRequest()
        if channel.user_id != request.team.user.id:
            return HttpResponseForbidden()

        new_checks = []
        for key in request.POST:
            if key.startswith("check-"):
                code = key[6:]
                try:
                    check = Check.objects.get(code=code)
                except Check.DoesNotExist:
                    return HttpResponseBadRequest()
                if check.user_id != request.team.user.id:
                    return HttpResponseForbidden()
                new_checks.append(check)

        channel.checks = new_checks
        return redirect("hc-channels")

    channels = Channel.objects.filter(user=request.team.user).order_by("created")
    channels = channels.annotate(n_checks=Count("checks"))

    num_checks = Check.objects.filter(user=request.team.user).count()

    ctx = {
        "page": "channels",
        "channels": channels,
        "num_checks": num_checks,
        "enable_pushbullet": settings.PUSHBULLET_CLIENT_ID is not None,
        "enable_pushover": settings.PUSHOVER_API_TOKEN is not None
    }
    return render(request, "front/channels.html", ctx)


def do_add_channel(request, data):
    form = AddChannelForm(data)
    if form.is_valid():
        channel = form.save(commit=False)
        channel.user = request.team.user
        channel.save()

        if request.user.id == request.team.user.id:
            channel.assign_all_checks()
        else:
            assigned_checks = []
            rows = AssignedChecks.objects.filter(user=request.user.id).order_by("created")
            for row in rows:
                assigned_checks.append(row.checks)

            channel.checks = assigned_checks

        if channel.kind == "email":
            channel.send_verify_link()

        return redirect("hc-channels")
    else:
        return HttpResponseBadRequest()


@login_required
def add_channel(request):
    assert request.method == "POST"
    return do_add_channel(request, request.POST)


@login_required
@uuid_or_400
def channel_checks(request, code):
    channel = get_object_or_404(Channel, code=code)
    if channel.user_id != request.team.user.id:
        return HttpResponseForbidden()

    assigned = set(channel.checks.values_list('code', flat=True).distinct())
    if(request.team.user.id == request.user.id):
        checks = Check.objects.filter(user=request.team.user).order_by("created")
    else:
        checks = []
        rows = AssignedChecks.objects.filter(user=request.user.id).order_by("created")
        for row in rows:
            checks.append(row.checks)

    ctx = {
        "checks": checks,
        "assigned": assigned,
        "channel": channel
    }

    return render(request, "front/channel_checks.html", ctx)


@uuid_or_400
def verify_email(request, code, token):
    channel = get_object_or_404(Channel, code=code)
    if channel.make_token() == token:
        channel.email_verified = True
        channel.save()
        return render(request, "front/verify_email_success.html")

    return render(request, "bad_link.html")


@login_required
@uuid_or_400
def remove_channel(request, code):
    assert request.method == "POST"

    # user may refresh the page during POST and cause two deletion attempts
    channel = Channel.objects.filter(code=code).first()
    if channel:
        if channel.user != request.team.user:
            return HttpResponseForbidden()
        channel.delete()

    return redirect("hc-channels")


@login_required
def add_email(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_email.html", ctx)


@login_required
def add_webhook(request):
    if request.method == "POST":
        form = AddWebhookForm(request.POST)
        if form.is_valid():
            channel = Channel(user=request.team.user, kind="webhook")
            channel.value = form.get_value()
            channel.save()

            channel.assign_all_checks()
            return redirect("hc-channels")
    else:
        form = AddWebhookForm()

    ctx = {"page": "channels", "form": form}
    return render(request, "integrations/add_webhook.html", ctx)


@login_required
def add_pd(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_pd.html", ctx)


def add_slack(request):
    if not settings.SLACK_CLIENT_ID and not request.user.is_authenticated:
        return redirect("hc-login")

    ctx = {
        "page": "channels",
        "slack_client_id": settings.SLACK_CLIENT_ID
    }
    return render(request, "integrations/add_slack.html", ctx)


@login_required
def add_slack_btn(request):
    code = request.GET.get("code", "")
    if len(code) < 8:
        return HttpResponseBadRequest()

    result = requests.post("https://slack.com/api/oauth.access", {
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
        "code": code
    })

    doc = result.json()
    if doc.get("ok"):
        channel = Channel()
        channel.user = request.team.user
        channel.kind = "slack"
        channel.value = result.text
        channel.save()
        channel.assign_all_checks()
        messages.success(request, "The Slack integration has been added!")
    else:
        s = doc.get("error")
        messages.warning(request, "Error message from slack: %s" % s)

    return redirect("hc-channels")


@login_required
def add_hipchat(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_hipchat.html", ctx)


@login_required
def add_pushbullet(request):
    if settings.PUSHBULLET_CLIENT_ID is None:
        raise Http404("pushbullet integration is not available")

    if "code" in request.GET:
        code = request.GET.get("code", "")
        if len(code) < 8:
            return HttpResponseBadRequest()

        result = requests.post("https://api.pushbullet.com/oauth2/token", {
            "client_id": settings.PUSHBULLET_CLIENT_ID,
            "client_secret": settings.PUSHBULLET_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        })

        doc = result.json()
        if "access_token" in doc:
            channel = Channel(kind="pushbullet")
            channel.user = request.team.user
            channel.value = doc["access_token"]
            channel.save()
            channel.assign_all_checks()
            messages.success(request,
                             "The Pushbullet integration has been added!")
        else:
            messages.warning(request, "Something went wrong")

        return redirect("hc-channels")

    redirect_uri = settings.SITE_ROOT + reverse("hc-add-pushbullet")
    authorize_url = "https://www.pushbullet.com/authorize?" + urlencode({
        "client_id": settings.PUSHBULLET_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code"
    })

    ctx = {
        "page": "channels",
        "authorize_url": authorize_url
    }
    return render(request, "integrations/add_pushbullet.html", ctx)


@login_required
def add_pushover(request):
    if settings.PUSHOVER_API_TOKEN is None or settings.PUSHOVER_SUBSCRIPTION_URL is None:
        raise Http404("pushover integration is not available")

    if request.method == "POST":
        # Initiate the subscription
        nonce = get_random_string()
        request.session["po_nonce"] = nonce

        failure_url = settings.SITE_ROOT + reverse("hc-channels")
        success_url = settings.SITE_ROOT + reverse("hc-add-pushover") + "?" + urlencode({
            "nonce": nonce,
            "prio": request.POST.get("po_priority", "0"),
        })
        subscription_url = settings.PUSHOVER_SUBSCRIPTION_URL + "?" + urlencode({
            "success": success_url,
            "failure": failure_url,
        })

        return redirect(subscription_url)

    # Handle successful subscriptions
    if "pushover_user_key" in request.GET:
        if "nonce" not in request.GET or "prio" not in request.GET:
            return HttpResponseBadRequest()

        # Validate nonce
        if request.GET["nonce"] != request.session.get("po_nonce"):
            return HttpResponseForbidden()

        # Validate priority
        if request.GET["prio"] not in ("-2", "-1", "0", "1", "2"):
            return HttpResponseBadRequest()

        # All looks well--
        del request.session["po_nonce"]

        if request.GET.get("pushover_unsubscribed") == "1":
            # Unsubscription: delete all Pushover channels for this user
            Channel.objects.filter(user=request.user, kind="po").delete()
            return redirect("hc-channels")
        else:
            # Subscription
            user_key = request.GET["pushover_user_key"]
            priority = int(request.GET["prio"])

            return do_add_channel(request, {
                "kind": "po",
                "value": "%s|%d" % (user_key, priority),
            })

    # Show Integration Settings form
    ctx = {
        "page": "channels",
        "po_retry_delay": td(seconds=settings.PUSHOVER_EMERGENCY_RETRY_DELAY),
        "po_expiration": td(seconds=settings.PUSHOVER_EMERGENCY_EXPIRATION),
    }
    return render(request, "integrations/add_pushover.html", ctx)


@login_required
def add_victorops(request):
    ctx = {"page": "channels"}
    return render(request, "integrations/add_victorops.html", ctx)


def privacy(request):
    return render(request, "front/privacy.html", {})


def terms(request):
    return render(request, "front/terms.html", {})


# frequently asked questions
def faq(request):
    frequently_asked_questions = FrequentlyAskedQuestion.objects.filter(status='s')
    message = None
    if request.method != "POST":
        form = FaqForm()
    form = FaqForm(request.POST)
    if form['email'].value() == '' or form['question'].value() == '':
        message = 'Question not sent due to invalid data'
    if form.is_valid():
        form.save()
        message = 'Thank you, we will get back to you' 
    
    return render(request, "front/faq.html", {
        "page":"faq",
        "form":form, 
        "message":message,
        "frequently_asked_questions":frequently_asked_questions
        })

@login_required
def departments(request):
    """ Display departments created by team members """
    depts = Department.objects.filter(user=request.team.user).order_by("created")

    ctx = {
        "page": "departments",
        "departments": depts
    }

    return render(request, "front/departments.html", ctx)

@login_required
def add_department(request):
    """ Add a new department to existing departments """
    if request.method == "POST":
        form = AddDepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.user = request.team.user
            department.save()
            messages.success(request, "New department has been added!")
            return redirect("hc-departments")
    else:
        form = AddDepartmentForm

    ctx = {"page": "add_department", "form": form}
    return render(request, "front/add_department.html", ctx)



