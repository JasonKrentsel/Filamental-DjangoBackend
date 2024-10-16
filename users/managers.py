from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.apps import apps
from django.db.transaction import atomic


class UserModelManager(BaseUserManager):
    # Create a user with a new organization
    @atomic
    def create_user(self, email: str, password: str, first_name: str, last_name: str):
        # validate email and password
        validate_email(email)
        validate_password(password)

        user = self.model(email=self.normalize_email(email),
                          first_name=first_name, last_name=last_name)
        user.set_password(password)

        UserProfileModel = apps.get_model('users', 'UserProfile')

        user.profile = UserProfileModel.objects.create()

        user.save(using=self._db)

        return user

    # Prevent the standard create method from being used
    def create(self, *args, **kwargs):
        raise NotImplementedError(
            "Use create_user() instead.")

    # Create a SUPERuser with a new organization
    @atomic
    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        user = self.create_user(email, password, first_name, last_name)

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)

        return user
