from django import forms
from django.contrib.auth.models import User
from quit_smoking_webapp.models import UserProfile, DailyLog, Emotion, Situation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput()
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return email

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match")

            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)

        return cleaned_data
    

class StartingPointForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cigarettes_per_day', 'pack_price', 'reason_to_quit', 'ranking_consent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cigarettes_per_day'].label = "How many cigarettes per day do you smoke?"
        self.fields['pack_price'].label = "Price of one pack of cigarettes"
        self.fields['reason_to_quit'].label = "Why do you want to quit smoking?"
        self.fields['ranking_consent'].label = "I agree to participate in the community ranking"


class UserProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Your password",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        required=False
    )
    password3 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['cigarettes_per_day', 'pack_price', 'reason_to_quit', 'ranking_consent']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['cigarettes_per_day'].label = "How many cigarettes per day do you smoke?"
        self.fields['pack_price'].label = "Price of one pack of cigarettes"
        self.fields['reason_to_quit'].label = "Why do you want to quit smoking?"
        self.fields['ranking_consent'].label = "I agree to participate in the community ranking"

    def clean(self):
        cleaned_data = super().clean()

        current = cleaned_data.get("password1")
        p1 = cleaned_data.get("password2")
        p2 = cleaned_data.get("password3")

        if not current and not p1 and not p2:
            return cleaned_data

        if not current or not p1 or not p2:
            raise forms.ValidationError("Fill all password fields to change password.")

        if not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")

        if p1 != p2:
            raise forms.ValidationError("New passwords do not match.")

        validate_password(p1, self.user)

        return cleaned_data

class DailyLogForm(forms.ModelForm):
    emotions_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "For example: stress, boredom, frustration"
        }),
        label="Emotions"
    )

    situations_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "For example: work, meeting, after meal"
        }),
        label="Situations"
    )

    class Meta:
        model = DailyLog
        fields = [
            "cigarettes_smoked",
            "smoke_free_day",
            "first_cigarette_time",
            "craving_level",
        ]
        widgets = {
            "first_cigarette_time": forms.TimeInput(attrs={"type": "time"})
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["first_cigarette_time"].required = False

    def clean_emotions_input(self):
        value = self.cleaned_data.get("emotions_input", "")
        return self._normalize_csv_text(value)

    def clean_situations_input(self):
        value = self.cleaned_data.get("situations_input", "")
        return self._normalize_csv_text(value)

    def clean(self):
        cleaned_data = super().clean()

        smoke_free_day = cleaned_data.get("smoke_free_day")
        cigarettes_smoked = cleaned_data.get("cigarettes_smoked")
        first_cigarette_time = cleaned_data.get("first_cigarette_time")
        emotions_input = cleaned_data.get("emotions_input", [])
        situations_input = cleaned_data.get("situations_input", [])

        if smoke_free_day:
            cleaned_data["cigarettes_smoked"] = 0
            cleaned_data["first_cigarette_time"] = None
            return cleaned_data

        if not emotions_input:
            self.add_error("emotions_input", "Add at least one emotion.")
        if not situations_input:
            self.add_error("situations_input", "Add at least one situation.")

        if cigarettes_smoked and cigarettes_smoked > 0 and not first_cigarette_time:
            self.add_error("first_cigarette_time", "First cigarette time is required if cigarettes smoked is greater than 0.")

        return cleaned_data

    def _normalize_csv_text(self, value):
        parts = [item.strip() for item in value.split(",")]
        parts = [item for item in parts if item]

        unique_parts = []
        seen = set()

        for item in parts:
            lowered = item.lower()
            if lowered not in seen:
                seen.add(lowered)
                unique_parts.append(item)

        return unique_parts


class SendPasswordResetLinkForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput()
    )


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    def clean(self):
            cleaned_data = super().clean()

            p1 = cleaned_data.get("password1")
            p2 = cleaned_data.get("password2")

            if p1 and p2 and p1 != p2:
                raise forms.ValidationError("Passwords do not match")
            
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)

            return cleaned_data
    
class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))