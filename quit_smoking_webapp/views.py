from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.functions import TruncDate
from django.db.models import Avg, Count, Sum
from quit_smoking_webapp.services.openai_chat import get_chatbot_reply
from quit_smoking_webapp.forms import RegisterForm, UserProfileForm, StartingPointForm, DailyLogForm, SendPasswordResetLinkForm, ResetPasswordForm, ChatForm
from quit_smoking_webapp.models import UserProfile, DailyLog, DailyLogEmotion, DailyLogSituation, ChatMessage, MotivationQuote, UserCustomEmotion, UserCustomSituation, Emotion, Situation
from collections import defaultdict
from django.core.paginator import Paginator
from statistics import mean
import json
from quit_smoking_webapp.helpers import is_htmx, calculate_ranking_score, assign_places, get_ranking_week_range, MIN_DAYS_REQUIRED
from quit_smoking_webapp.statistics_helpers import get_consumption_stats, get_emotion_stats, get_trigger_stats

def welcome_view(request):
    return render(request, 'welcome.html', {'is_authenticated': request.user.is_authenticated})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "GET":
        form = RegisterForm()
    else:
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.data["username"],
                email = form.data["email"],
                password = form.data['password1']
            )

            return redirect('login')

    return render(request, 'register.html', {'form': form})


def login_view(request):  
    if request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "GET":
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            return redirect('dashboard')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    has_profile = UserProfile.objects.filter(user=request.user).exists()
    form = None

    if not has_profile:
        if request.method == "GET":
            form = StartingPointForm()
        else:
            form = StartingPointForm(request.POST)

            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                has_profile = True

    logs = DailyLog.objects.filter(user=request.user).order_by("created_at")
    profile = UserProfile.objects.filter(user=request.user).first()

    total_logs = logs.count()
    smoke_free_days = logs.filter(smoke_free_day=True).count()
    avg_cigarettes = logs.aggregate(avg=Avg("cigarettes_smoked"))["avg"] or 0
    total_cigarettes = logs.aggregate(total=Sum("cigarettes_smoked"))["total"] or 0

    daily_stats = (
        logs.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            cigarettes_sum=Sum("cigarettes_smoked"),
            logs_count=Count("id"),
            smoke_free_count=Count("id", filter=None),
        )
        .order_by("day")
    )

    chart_labels = []
    chart_cigarettes = []

    for row in daily_stats:
        chart_labels.append(row["day"].strftime("%Y-%m-%d"))
        chart_cigarettes.append(row["cigarettes_sum"])

    smoking_days = total_logs - smoke_free_days

    context = {
        "has_profile": has_profile,
        "profile": profile,
        "form": form,
        "log_number": total_logs,
        "total_logs": total_logs,
        "smoke_free_days": smoke_free_days,
        "avg_cigarettes": round(avg_cigarettes, 2),
        "total_cigarettes": total_cigarettes,
        "chart_labels_json": json.dumps(chart_labels),
        "chart_cigarettes_json": json.dumps(chart_cigarettes),
        "smoke_free_days_json": json.dumps(smoke_free_days),
        "smoking_days_json": json.dumps(smoking_days),
        "active_menu": "dashboard",
    }

    return render(request, "dashboard.html", context)

 
@login_required
def dashboard_shell(request):
    return render(request, "dashboard_shell.html")


@login_required
def ui_home(request):
    consumption_context = get_consumption_stats(request.user)
    emotion_context = get_emotion_stats(request.user)
    trigger_context = get_trigger_stats(request.user)

    motivation_quote = MotivationQuote.objects.order_by("?").select_related("quote_type").first()

    context = {
        **consumption_context,
        **emotion_context,
        **trigger_context,
         "motivation_quote": motivation_quote,
    }

    if is_htmx(request):
        return render(request, "partials/ui_home.html", context)

    return render(request, "dashboard.html", {
        "has_profile": True,
        "content_template": "partials/ui_home.html",
        "active_menu": "dashboard",
        **context,
    })


@login_required
def ui_starting_point(request):   
    if request.method == "GET":
        form = StartingPointForm()
    else:
        form = StartingPointForm(request.POST)
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    
    if is_htmx(request):
        return render(request, "partials/ui_starting_point.html", {'form': form})
    else:
        return render(request, "dashboard.html", {
            "has_profile": False,
            "content_template": "partials/ui_starting_point.html",
            "form": form
        })


@login_required
def ui_daily_log(request):
    if not is_htmx(request):
        return redirect("dashboard")
    
    if not UserProfile.objects.filter(user=request.user).exists():
        return redirect("dashboard")

    logs_list = DailyLog.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(logs_list, 10)

    page_number = request.GET.get("page")
    logs = paginator.get_page(page_number)

    return render(request, "partials/ui_daily_log.html", {"logs": logs})


@login_required
def ui_profile(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if not profile:
        return redirect('dashboard')

    if request.method == "GET":
        form = UserProfileForm(instance=profile)
    else:
        form = UserProfileForm(request.POST, user=request.user, instance=profile)

        if form.is_valid():
            profile.user = request.user
            profile.save()
            request.user.save()

            new_password = form.cleaned_data.get("password2")
            if new_password:
                request.user.set_password(form.cleaned_data["password2"])
                request.user.save()
                login(request, request.user)

            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")

            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })

    if is_htmx(request):
        return render(request, 'partials/ui_profile.html', {'form': form})
    else:
        return render(request, 'dashboard.html', {
            "has_profile": True,
            "content_template": "partials/ui_profile.html",
            "form": form
        })

def save_log_emotions_for_user(daily_log, user, emotion_names):
    default_emotions = {
        emotion.name.lower(): emotion
        for emotion in Emotion.objects.all()
    }

    for name in emotion_names:
        normalized = name.strip()
        if not normalized:
            continue

        default_match = default_emotions.get(normalized.lower())

        if default_match:
            DailyLogEmotion.objects.create(
                daily_log=daily_log,
                emotion=default_match
            )
        else:
            DailyLogEmotion.objects.create(
                daily_log=daily_log,
                custom_emotion=normalized
            )
            UserCustomEmotion.objects.get_or_create(
                user=user,
                name=normalized
            )


def save_log_situations_for_user(daily_log, user, situation_names):
    default_situations = {
        situation.name.lower(): situation
        for situation in Situation.objects.all()
    }

    for name in situation_names:
        normalized = name.strip()
        if not normalized:
            continue

        default_match = default_situations.get(normalized.lower())

        if default_match:
            DailyLogSituation.objects.create(
                daily_log=daily_log,
                situation=default_match
            )
        else:
            DailyLogSituation.objects.create(
                daily_log=daily_log,
                custom_situation=normalized
            )
            UserCustomSituation.objects.get_or_create(
                user=user,
                name=normalized
            )

@login_required
def ui_add_daily_log_view(request):
    if not UserProfile.objects.filter(user=request.user).exists():
        return redirect("dashboard")

    if request.method == "GET":
        form = DailyLogForm(user=request.user)
    else:
        form = DailyLogForm(request.POST, user=request.user)

        if form.is_valid():
            daily_log = form.save(commit=False)
            daily_log.user = request.user
            daily_log.save()

            if not daily_log.smoke_free_day:
                save_log_emotions_for_user(
                    daily_log,
                    request.user,
                    form.cleaned_data["emotions_input"]
                )
                save_log_situations_for_user(
                    daily_log,
                    request.user,
                    form.cleaned_data["situations_input"]
                )

            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")

            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })

    emotion_suggestions = list(Emotion.objects.values_list("name", flat=True)) + list(
        UserCustomEmotion.objects.filter(user=request.user).values_list("name", flat=True)
    )
    situation_suggestions = list(Situation.objects.values_list("name", flat=True)) + list(
        UserCustomSituation.objects.filter(user=request.user).values_list("name", flat=True)
    )

    context = {
        "form": form,
        "emotion_suggestions": sorted(set(emotion_suggestions)),
        "situation_suggestions": sorted(set(situation_suggestions)),
    }

    if is_htmx(request):
        return render(request, "partials/ui_add_daily_log.html", context)
    else:
        return render(request, "dashboard.html", {
            "has_profile": True,
            "content_template": "partials/ui_add_daily_log.html",
            **context,
        })


@login_required
def ui_edit_daily_log_view(request, log_id):
    if not UserProfile.objects.filter(user=request.user).exists():
        return redirect("dashboard")

    daily_log = get_object_or_404(DailyLog, id=log_id, user=request.user)

    if request.method == "GET":
        daily_log_emotions = DailyLogEmotion.objects.filter(daily_log=daily_log).select_related("emotion")
        daily_log_situations = DailyLogSituation.objects.filter(daily_log=daily_log).select_related("situation")

        emotion_names = []
        for item in daily_log_emotions:
            if item.emotion:
                emotion_names.append(item.emotion.name)
            elif item.custom_emotion:
                emotion_names.append(item.custom_emotion)

        situation_names = []
        for item in daily_log_situations:
            if item.situation:
                situation_names.append(item.situation.name)
            elif item.custom_situation:
                situation_names.append(item.custom_situation)

        initial = {
            "emotions_input": ", ".join(emotion_names),
            "situations_input": ", ".join(situation_names),
        }

        form = DailyLogForm(instance=daily_log, initial=initial, user=request.user)
    else:
        form = DailyLogForm(request.POST, instance=daily_log, user=request.user)

        if form.is_valid():
            daily_log = form.save()

            DailyLogEmotion.objects.filter(daily_log=daily_log).delete()
            DailyLogSituation.objects.filter(daily_log=daily_log).delete()

            if not daily_log.smoke_free_day:
                save_log_emotions_for_user(
                    daily_log,
                    request.user,
                    form.cleaned_data["emotions_input"]
                )
                save_log_situations_for_user(
                    daily_log,
                    request.user,
                    form.cleaned_data["situations_input"]
                )

            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")
            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })

    emotion_suggestions = list(Emotion.objects.values_list("name", flat=True)) + list(
        UserCustomEmotion.objects.filter(user=request.user).values_list("name", flat=True)
    )
    situation_suggestions = list(Situation.objects.values_list("name", flat=True)) + list(
        UserCustomSituation.objects.filter(user=request.user).values_list("name", flat=True)
    )

    context = {
        "form": form,
        "daily_log": daily_log,
        "emotion_suggestions": sorted(set(emotion_suggestions)),
        "situation_suggestions": sorted(set(situation_suggestions)),
    }

    if is_htmx(request):
        return render(request, "partials/ui_edit_daily_log.html", context)
    else:
        return render(request, "dashboard.html", {
            "has_profile": True,
            "content_template": "partials/ui_edit_daily_log.html",
            **context,
        })


@login_required
def ui_delete_log_view(request, log_id):
    if not is_htmx(request):
        return redirect("dashboard")
    
    if UserProfile.objects.filter(user=request.user).exists() == False:
        return redirect('dashboard')
    
    daily_log = get_object_or_404(DailyLog, id=log_id, user=request.user)

    if request.method == "POST":
        daily_log.delete()

        logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")
        return render(request, "partials/ui_daily_log.html", {"logs": logs})
    
    return render(
        request,
        'partials/ui_delete_daily_log.html',
        {'log': daily_log}
    )


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return redirect("welcome")
    return redirect("ui_profile")


def password_reset_view(request):
    if request.method == "GET":
        form = SendPasswordResetLinkForm()

        return render(request, 'password_reset.html', {'form': form})
    else:
        form  = SendPasswordResetLinkForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(email=form.data["email"]).first()

            if user is not None:
                token = default_token_generator.make_token(user)
                uid = user.pk

                message = f'Click this link to reset a password: https:///password-reset/{uid}/{token}'

                print(message)

                send_mail(
                    subject="Reset your password",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email]
                )

        return render(request, 'password_reset_done.html') 


def password_reset_confirm_view(request, uidb64, token):
    if request.method == "GET":
        form = ResetPasswordForm()
        return render(request, 'password_reset_confirm.html', {'form': form}) 
    else:
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(pk=uidb64).first()

            if user is not None:
                if default_token_generator.check_token(user, token) == True:
                    user.set_password(form.data['password1'])
                    user.save()

                    return redirect("login")
                else:
                    return render(request, 'password_reset_confirm.html', {'form': form}) 
        else:
            return render(request, 'password_reset_confirm.html', {'form': form}) 
        

@login_required
def ui_chat(request):
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")

    form = ChatForm()

    if is_htmx(request):
        return render(request, "partials/ui_chat.html", {
            "form": form,
            "chat_messages": chat_messages
        })
    else:
        return render(request, "dashboard.html", {
            "has_profile": True,
            "content_template": "partials/ui_chat.html",
            "form": form,
            "chat_messages": chat_messages
        }) 
    

@login_required
def send_chat_message(request):
    if request.method != "POST":
        return redirect('ui_chat')
    
    form = ChatForm(request.POST)
    chat_messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")

    if not form.is_valid():
        if is_htmx(request):
            return render(request, "partials/ui_chat.html", {
                "form": form,
                "chat_messages": chat_messages
            })
        return redirect('ui_chat')

    user_message = form.cleaned_data["message"].strip()
    previous_messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")
    
    chat_history = []
    for chat in previous_messages:
        role = "Assistant" if chat.is_chat_response else "User"
        chat_history.append(f"{role}: {chat.message}")

    ChatMessage.objects.create(
        user=request.user,
        message=user_message,
        is_chat_response=False
    )

    chat_reply = get_chatbot_reply(user_message, chat_history)

    ChatMessage.objects.create(
        user=request.user,
        message=chat_reply,
        is_chat_response=True
    )

    chat_messages = ChatMessage.objects.filter(user=request.user).order_by("created_at")

    form = ChatForm()

    if is_htmx(request):
        return render(request, "partials/ui_chat.html", {
            "form": form,
            "chat_messages": chat_messages
        })
    
    return redirect('ui_chat')


@login_required
def ui_ranking(request):
    week_start, week_end = get_ranking_week_range()

    logs = (
        DailyLog.objects
        .select_related("user")
        .filter(
            created_at__date__range=[week_start, week_end],
            user__userprofile__ranking_consent=True
        )
        .only(
            "user__id",
            "user__username",
            "created_at",
            "cigarettes_smoked",
            "smoke_free_day",
        )
    )

    grouped = defaultdict(lambda: {
        "username": "",
        "days": {}
    })

    for log in logs.iterator():
        user_data = grouped[log.user_id]
        user_data["username"] = log.user.username

        day = log.created_at.date()

        day_data = user_data["days"].setdefault(day, {
            "cigarettes_sum": 0,
            "smoke_free": True,
        })

        day_data["cigarettes_sum"] += log.cigarettes_smoked

        if not log.smoke_free_day:
            day_data["smoke_free"] = False

    eligible_ranking = []
    ineligible_ranking = []

    for user_id, data in grouped.items():
        daily_entries = list(data["days"].values())
        daily_totals = [entry["cigarettes_sum"] for entry in daily_entries]

        days_count = len(daily_entries)
        smoke_free_days = sum(1 for entry in daily_entries if entry["smoke_free"])
        total_cigarettes = sum(daily_totals)
        avg_daily_cigarettes = mean(daily_totals) if daily_totals else 0

        score, smoke_free_ratio = calculate_ranking_score(
            avg_daily_cigarettes=avg_daily_cigarettes,
            smoke_free_days=smoke_free_days,
            days_count=days_count,
        )

        entry = {
            "user_id": user_id,
            "username": data["username"],
            "days_count": days_count,
            "smoke_free_days": smoke_free_days,
            "smoke_free_ratio": smoke_free_ratio,
            "total_cigarettes": total_cigarettes,
            "avg_daily_cigarettes": round(avg_daily_cigarettes, 2),
            "score": score,
            "eligible": days_count >= MIN_DAYS_REQUIRED,
            "place": None,
        }

        if entry["eligible"]:
            eligible_ranking.append(entry)
        else:
            ineligible_ranking.append(entry)

    eligible_ranking.sort(key=lambda x: (
        -x["score"],
        -x["smoke_free_ratio"],
        x["avg_daily_cigarettes"],
        -x["days_count"],
        x["username"].lower(),
    ))

    ineligible_ranking.sort(key=lambda x: (
        -x["days_count"],
        x["avg_daily_cigarettes"],
        x["username"].lower(),
    ))

    ranking = assign_places(eligible_ranking) + ineligible_ranking

    current_user_place = None
    current_user_entry = None

    for entry in ranking:
        if entry["user_id"] == request.user.id:
            current_user_entry = entry
            current_user_place = entry["place"]
            break

    ranking_top_10 = ranking[:10]

    context = {
        "ranking": ranking_top_10,
        "min_days_required": MIN_DAYS_REQUIRED,
        "current_user_place": current_user_place,
        "current_user_entry": current_user_entry,
    }

    if is_htmx(request):
        return render(request, "partials/ui_ranking.html", context)

    return render(request, "dashboard.html", {
        "has_profile": True,
        "content_template": "partials/ui_ranking.html",
        "active_menu": "ranking",
        **context,
    })