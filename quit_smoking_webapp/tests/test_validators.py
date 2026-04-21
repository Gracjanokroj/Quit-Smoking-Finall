from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from quit_smoking_webapp.validators import CustomPasswordValidator


class CustomPasswordValidatorTest(SimpleTestCase):
    def setUp(self):
        self.validator = CustomPasswordValidator()

    def test_valid_password_passes(self):
        self.validator.validate("Xk9mPqL2!")

    def test_missing_uppercase_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("xk9mpql2!")
        self.assertIn("uppercase", str(ctx.exception))

    def test_missing_lowercase_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("XK9MPQL2!")
        self.assertIn("lowercase", str(ctx.exception))

    def test_missing_digit_raises(self):
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate("XkmPqLab!")
        self.assertIn("digit", str(ctx.exception))

    def test_get_help_text_mentions_requirements(self):
        text = self.validator.get_help_text()
        self.assertIn("uppercase", text)
        self.assertIn("lowercase", text)
        self.assertIn("digit", text)
