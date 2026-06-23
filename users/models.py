from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import random
from PIL import Image, ImageDraw,ImageFont
from io import BytesIO
from django.core.files.base import ContentFile
from pathlib import Path

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
    
    colors = [
        (100, 149, 237), (144, 238, 144), (255, 182, 193),
        (255, 218, 185), (221, 160, 221), (176, 224, 230),
        (240, 230, 140), (255, 160, 122),
    ]
    bg_color = random.choice(colors)
    
    img = Image.new("RGB", (200, 200), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    font_path = BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
    try:
        font = ImageFont.truetype(str(font_path), 80)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (200 - text_width) // 2
    y = (200 - text_height) // 2
    
    draw.text((x, y), initial, fill="white", font=font)
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return ContentFile(buffer.getvalue(), name=f"avatar_{timezone.now().timestamp()}.png")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name="Favorite projects"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
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
        return self.project_set.all()

    @property
    def participated_projects(self):
        return self.participated_projects.all()