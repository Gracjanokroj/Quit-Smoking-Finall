from django.db import models
from django.contrib.auth.models import User


class MotivationQuoteType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class MotivationQuote(models.Model):
    text = models.TextField()
    author = models.CharField(max_length=100)
    quote_type = models.ForeignKey(MotivationQuoteType, on_delete=models.CASCADE)

    def __str__(self):
        return self.text[:50]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    cigarettes_per_day = models.PositiveIntegerField()
    pack_price = models.DecimalField(max_digits=6, decimal_places=2)
    reason_to_quit = models.TextField()
    ranking_consent = models.BooleanField(default=False)
    updated_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class CravingLevel(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Emotion(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Situation(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    cigarettes_smoked = models.PositiveIntegerField()
    smoke_free_day = models.BooleanField()

    first_cigarette_time = models.TimeField(null=True, blank=True)

    craving_level = models.ForeignKey(CravingLevel, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.date()}"

class UserCustomEmotion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class UserCustomSituation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
class DailyLogEmotion(models.Model):
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)
    emotion = models.ForeignKey(Emotion, on_delete=models.CASCADE, null=True, blank=True)
    custom_emotion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.daily_log} - {self.display_name}"

    @property
    def display_name(self):
        if self.emotion:
            return self.emotion.name
        return self.custom_emotion

    class Meta:
        pass


class DailyLogSituation(models.Model):
    daily_log = models.ForeignKey(DailyLog, on_delete=models.CASCADE)
    situation = models.ForeignKey(Situation, on_delete=models.CASCADE, null=True, blank=True)
    custom_situation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.daily_log} - {self.display_name}"

    @property
    def display_name(self):
        if self.situation:
            return self.situation.name
        return self.custom_situation

    class Meta:
        pass


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_chat_response = models.BooleanField()

    def __str__(self):
        who = "Bot" if self.is_chat_response else "User"
        return f"{who}: {self.message[:40]}"