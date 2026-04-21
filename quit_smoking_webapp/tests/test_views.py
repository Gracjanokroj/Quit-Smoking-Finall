from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from quit_smoking_webapp.models import (
    UserProfile,
    CravingLevel,
    DailyLog,
    Emotion,
    Situation,
)


class WelcomeViewTest(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse("welcome"))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_is_not_authenticated_in_context(self):
        response = self.client.get(reverse("welcome"))
        self.assertFalse(response.context["is_authenticated"])

    def test_authenticated_user_flag_in_context(self):
        user = User.objects.create_user("u", password="pass")
        self.client.force_login(user)
        response = self.client.get(reverse("welcome"))
        self.assertTrue(response.context["is_authenticated"])


class RegisterViewTest(TestCase):
    def _valid_post(self):
        return {
            "username": "newuser",
            "email": "new@example.com",
            "password1": "Xk9mPqL2!",
            "password2": "Xk9mPqL2!",
        }

    def test_get_renders_form(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_valid_post_creates_user_and_redirects_to_login(self):
        response = self.client.post(reverse("register"), self._valid_post())
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_duplicate_email_returns_form_with_error(self):
        User.objects.create_user("existing", email="new@example.com", password="x")
        response = self.client.post(reverse("register"), self._valid_post())
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

    def test_password_mismatch_returns_form_with_error(self):
        data = self._valid_post()
        data["password2"] = "Different99!"
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

    def test_authenticated_user_redirected_to_dashboard(self):
        user = User.objects.create_user("u", password="pass")
        self.client.force_login(user)
        response = self.client.get(reverse("register"))
        self.assertRedirects(response, reverse("dashboard"))


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="Xk9mPqL2!")

    def test_get_renders_form(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_valid_credentials_redirect_to_dashboard(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "Xk9mPqL2!"}
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_invalid_credentials_returns_form_with_error(self):
        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("logoutuser", password="pass")

    def test_logout_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))

    def test_after_logout_dashboard_requires_login(self):
        self.client.force_login(self.user)
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])


class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("dashuser", password="pass")

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_without_profile_shows_starting_point_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_profile"])
        self.assertIsNotNone(response.context["form"])

    def test_with_profile_hides_starting_point_form(self):
        UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_profile"])
        self.assertIsNone(response.context["form"])


class UiAddDailyLogViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("loguser", password="pass")
        self.craving_level = CravingLevel.objects.create(name="Low")
        self.profile = UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse("ui_daily_log_add"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_without_profile_redirects_to_dashboard(self):
        other_user = User.objects.create_user("noprofile", password="pass")
        self.client.force_login(other_user)
        response = self.client.get(reverse("ui_daily_log_add"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_get_with_profile_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("ui_daily_log_add"))
        self.assertEqual(response.status_code, 200)

    def test_post_smoke_free_creates_log(self):
        self.client.force_login(self.user)
        data = {
            "cigarettes_smoked": 0,
            "smoke_free_day": True,
            "first_cigarette_time": "",
            "craving_level": self.craving_level.id,
            "emotions_input": "",
            "situations_input": "",
        }
        response = self.client.post(reverse("ui_daily_log_add"), data)
        self.assertEqual(response.status_code, 200)
        log = DailyLog.objects.get(user=self.user)
        self.assertTrue(log.smoke_free_day)
        self.assertEqual(log.cigarettes_smoked, 0)

    def test_post_non_smoke_free_creates_log_with_emotions_and_situations(self):
        Emotion.objects.create(name="Stress")
        Situation.objects.create(name="Work")
        self.client.force_login(self.user)
        data = {
            "cigarettes_smoked": 5,
            "smoke_free_day": False,
            "first_cigarette_time": "08:00",
            "craving_level": self.craving_level.id,
            "emotions_input": "Stress, custom_feeling",
            "situations_input": "Work, custom_trigger",
        }
        response = self.client.post(reverse("ui_daily_log_add"), data)
        self.assertEqual(response.status_code, 200)
        log = DailyLog.objects.get(user=self.user)
        self.assertEqual(log.cigarettes_smoked, 5)
        self.assertFalse(log.smoke_free_day)
        self.assertEqual(log.dailylogemotion_set.count(), 2)
        self.assertEqual(log.dailylogsituation_set.count(), 2)

    def test_post_invalid_data_returns_form_with_errors(self):
        self.client.force_login(self.user)
        data = {
            "cigarettes_smoked": 5,
            "smoke_free_day": False,
            "first_cigarette_time": "",
            "craving_level": self.craving_level.id,
            "emotions_input": "",
            "situations_input": "",
        }
        response = self.client.post(reverse("ui_daily_log_add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(DailyLog.objects.filter(user=self.user).count(), 0)


class UiDeleteLogViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("deluser", password="pass")
        self.craving_level = CravingLevel.objects.create(name="Low")
        UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )
        self.log = DailyLog.objects.create(
            user=self.user,
            cigarettes_smoked=0,
            smoke_free_day=True,
            craving_level=self.craving_level,
        )

    def test_non_htmx_request_redirects_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("ui_daily_log_delete", args=[self.log.id])
        )
        self.assertRedirects(response, reverse("dashboard"))

    def test_htmx_get_shows_confirmation(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("ui_daily_log_delete", args=[self.log.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)

    def test_htmx_post_deletes_log_and_returns_list(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("ui_daily_log_delete", args=[self.log.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(DailyLog.objects.filter(id=self.log.id).exists())

    def test_cannot_delete_another_users_log(self):
        other_user = User.objects.create_user("other", password="pass")
        UserProfile.objects.create(
            user=other_user,
            cigarettes_per_day=5,
            pack_price=Decimal("10.00"),
            reason_to_quit="Health",
        )
        self.client.force_login(other_user)
        response = self.client.post(
            reverse("ui_daily_log_delete", args=[self.log.id]),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)


class UiDailyLogViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("listuser", password="pass")
        UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )

    def test_non_htmx_redirects_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("ui_daily_log"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_htmx_returns_200_with_logs(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("ui_daily_log"), HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn("logs", response.context)


class UiProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("profuser", password="Xk9mPqL2!")
        self.profile = UserProfile.objects.create(
            user=self.user,
            cigarettes_per_day=10,
            pack_price=Decimal("15.00"),
            reason_to_quit="Health",
        )

    def test_without_profile_redirects_to_dashboard(self):
        other = User.objects.create_user("noprof", password="pass")
        self.client.force_login(other)
        response = self.client.get(reverse("ui_profile"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_get_renders_profile_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("ui_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_valid_post_updates_profile(self):
        self.client.force_login(self.user)
        data = {
            "cigarettes_per_day": 15,
            "pack_price": "20.00",
            "reason_to_quit": "Updated reason",
            "ranking_consent": False,
            "password1": "",
            "password2": "",
            "password3": "",
        }
        self.client.post(reverse("ui_profile"), data)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.cigarettes_per_day, 15)
