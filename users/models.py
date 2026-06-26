import random
from PIL import Image, ImageDraw,ImageFont
from io import BytesIO
from pathlib import Path

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

from constants import colors, AVATAR_MODE, AVATAR_SIZE, FORM_MAX_LENGTH,\
 USER_MODEL_NAME_MAX_LENGTH, USER_MODEL_SURNAME_MAX_LENGTH, USER_MODEL_PHONE_NUMBER_MAX_LENGTH,\
 USER_MODEL_ABOUT_MAX_LENGTH, USER_MODEL_EMAIL_MAX_LENGTH, FONT_SIZE


BASE_DIR = Path(__file__).resolve().parent.parent


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


def generate_avatar(name, surname):
    """Generate avatar with first letter of name on colored background"""
    initial = (name[0] if name else surname[0] if surname else "U").upper()
    
    
    bg_color = random.choice(colors)
    
    img = Image.new(AVATAR_MODE, AVATAR_SIZE, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    font_path = BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    try:
        font = ImageFont.truetype(str(font_path), FONT_SIZE)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", FONT_SIZE)
        except:
            font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (AVATAR_SIZE[0] - text_width) // 2
    y = (AVATAR_SIZE[1] - text_height) // 2
    
    draw.text((x, y), initial, fill="white", font=font)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return ContentFile(buffer.getvalue(), name=f"avatar_{timezone.now().timestamp()}.png")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True, 
        max_length=USER_MODEL_EMAIL_MAX_LENGTH,
        verbose_name=_("Электронная почта")
    )
    name = models.CharField(
        max_length=USER_MODEL_NAME_MAX_LENGTH,
        verbose_name=_("Имя")
    )
    surname = models.CharField(
        max_length=USER_MODEL_SURNAME_MAX_LENGTH,
        verbose_name=_("Фамилия")
    )
    avatar = models.ImageField(
        upload_to="avatars/", 
        blank=True, 
        null=True,
        verbose_name=_("Аватар")
    )
    phone = models.CharField(
        max_length=USER_MODEL_PHONE_NUMBER_MAX_LENGTH, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name=_("Номер телефона")
    )
    github_url = models.URLField(
        blank=True, 
        null=True,
        verbose_name=_("Ссылка на GitHub")
    )
    about = models.TextField(
        max_length=USER_MODEL_ABOUT_MAX_LENGTH, 
        blank=True, 
        null=True,
        verbose_name=_("О себе")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Активен")
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("Статус персонала")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата регистрации")
    )

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name=_("Избранные проекты")
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"

    def save(self, *args, **kwargs):
        if not self.avatar and self.name:
            self.avatar = generate_avatar(self.name, self.surname)

        if self.phone:
            self.phone = self.normalize_phone(self.phone)

        super().save(*args, **kwargs)

    @staticmethod
    def normalize_phone(phone):
        digits = "".join(filter(str.isdigit, phone))
        if len(digits) == 11 and digits.startswith("7"):
            return f"+{digits}"
        elif len(digits) == 11 and digits.startswith("8"):
            return f"+7{digits[1:]}"
        elif len(digits) == 10:
            return f"+7{digits}"
        return phone

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"

    @property
    def owned_projects(self):     
        return self.owned_projects.all() 

    @property
    def participated_projects(self):
        return self.participated_projects.all() 

