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
    def create_superuser(self, email, password, organization_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user_with_new_organization(
            email, password, organization_name)
        for key, value in extra_fields.items():
            setattr(user, key, value)
        user.save(using=self._db)
        return user
