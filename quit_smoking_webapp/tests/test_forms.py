from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from quit_smoking_webapp.forms import (
    RegisterForm,
    DailyLogForm,
    UserProfileForm,
    ResetPasswordForm,
)
from quit_smoking_webapp.models import UserProfile, CravingLevel


class RegisterFormTest(TestCase):
    def _valid_data(self):
        return {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Xk9mPqL2!",
            "password2": "Xk9mPqL2!",
        }

    def test_valid_data_is_valid(self):
        form = RegisterForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(username="existing", email="new@example.com", password="x")
        form = RegisterForm(data=self._valid_data())
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch_is_invalid(self):
        data = self._valid_data()
        data["password2"] = "Different99!"
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_missing_uppercase_is_invalid(self):
        data = self._valid_data()
        data["password1"] = data["password2"] = "xk9mpql2!"
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_too_short_is_invalid(self):
        data = self._valid_data()
        data["password1"] = data["password2"] = "Xk9!"
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())


class DailyLogFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="pass")
        self.craving_level = CravingLevel.objects.create(name="Low")

    def _base_data(self, **overrides):
        data = {
            "cigarettes_smoked": 5,
            "smoke_free_day": False,
            "first_cigarette_time": "08:00",
            "craving_level": self.craving_level.id,
            "emotions_input": "stress",
            "situations_input": "work",
        }
        data.update(overrides)
        return data

    def test_valid_non_smoke_free_is_valid(self):
        form = DailyLogForm(data=self._base_data(), user=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_smoke_free_day_zeros_cigarettes_and_clears_time(self):
        data = self._base_data(
            smoke_free_day=True,
            cigarettes_smoked=10,
            first_cigarette_time="",
            emotions_input="",
            situations_input="",
        )
        form = DailyLogForm(data=data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["cigarettes_smoked"], 0)
        self.assertIsNone(form.cleaned_data["first_cigarette_time"])

    def test_non_smoke_free_without_emotions_is_invalid(self):
        form = DailyLogForm(data=self._base_data(emotions_input=""), user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("emotions_input", form.errors)

    def test_non_smoke_free_without_situations_is_invalid(self):
        form = DailyLogForm(data=self._base_data(situations_input=""), user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("situations_input", form.errors)

    def test_cigarettes_without_first_time_is_invalid(self):
        form = DailyLogForm(
            data=self._base_data(cigarettes_smoked=5, first_cigarette_time=""),
            user=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("first_cigarette_time", form.errors)

    def test_csv_deduplication_case_insensitive(self):
        form = DailyLogForm(
            data=self._base_data(emotions_input="stress, Stress, boredom"),
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["emotions_input"], ["stress", "boredom"])

    def test_csv_whitespace_stripped(self):
        form = DailyLogForm(
            data=self._base_data(situations_input="  work  ,  coffee  "),
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["situations_input"], ["work", "coffee"])

    def test_empty_csv_entries_ignored(self):
        form = DailyLogForm(
            data=self._base_data(emotions_input="stress,,, ,boredom"),
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["emotions_input"], ["stress", "boredom"])


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            password="Xk9mPqL2!",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )

    def _base_data(self, **overrides):
        data = {
            "cigarettes_per_day": 10,
            "pack_price": "15.00",
            "reason_to_quit": "Health",
            "ranking_consent": False,
            "password1": "",
            "password2": "",
            "password3": "",
        }
        data.update(overrides)
        return data

    def test_no_password_change_is_valid(self):
        form = UserProfileForm(data=self._base_data(), user=self.user, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)

    def test_partial_password_fields_invalid(self):
        form = UserProfileForm(
            data=self._base_data(password1="Xk9mPqL2!", password2=""),
            user=self.user,
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())

    def test_wrong_current_password_invalid(self):
        form = UserProfileForm(
            data=self._base_data(
                password1="WrongPass1!",
                password2="NewPass99!",
                password3="NewPass99!",
            ),
            user=self.user,
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())

    def test_new_password_mismatch_invalid(self):
        form = UserProfileForm(
            data=self._base_data(
                password1="Xk9mPqL2!",
                password2="NewPass99!",
                password3="NewPass00!",
            ),
            user=self.user,
            instance=self.profile,
        )
        self.assertFalse(form.is_valid())

    def test_valid_password_change_is_valid(self):
        form = UserProfileForm(
            data=self._base_data(
                password1="Xk9mPqL2!",
                password2="NewPass99!",
                password3="NewPass99!",
            ),
            user=self.user,
            instance=self.profile,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["password2"], "NewPass99!")


class ResetPasswordFormTest(TestCase):
    def test_matching_valid_passwords_is_valid(self):
        form = ResetPasswordForm(data={"password1": "Xk9mPqL2!", "password2": "Xk9mPqL2!"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_mismatching_passwords_invalid(self):
        form = ResetPasswordForm(data={"password1": "Xk9mPqL2!", "password2": "Different1!"})
        self.assertFalse(form.is_valid())

    def test_weak_password_invalid(self):
        form = ResetPasswordForm(data={"password1": "weakpass", "password2": "weakpass"})
        self.assertFalse(form.is_valid())
