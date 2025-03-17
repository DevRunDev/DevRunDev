from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-6_i*5p2r4jkx=p(9rip@arle=kg4u5gf+1enm5j1-hu@8#5&t*"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.kakao",
    "allauth.socialaccount.providers.naver",
    "debug_toolbar",
    "django_extensions",
    "accounts",
    "courses",
    "enrollments",
    "videos",
    "payments",
    "reviews",
    "qna",
    "notifications",
    "admin_panel",
    "quizzes",
    "core",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom user model

AUTH_USER_MODEL = "accounts.User"


# Allauth settings

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default="")

KAKAO_CLIENT_ID = env("KAKAO_CLIENT_ID", default="")
KAKAO_CLIENT_SECRET = env("KAKAO_CLIENT_SECRET", default="")

NAVER_CLIENT_ID = env("NAVER_CLIENT_ID", default="")
NAVER_CLIENT_SECRET = env("NAVER_CLIENT_SECRET", default="")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ImproperlyConfigured("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required.")

if not KAKAO_CLIENT_ID or not KAKAO_CLIENT_SECRET:
    raise ImproperlyConfigured("KAKAO_CLIENT_ID and KAKAO_CLIENT_SECRET are required.")

if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    raise ImproperlyConfigured("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are required.")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_CLIENT_ID,
            "secret": GOOGLE_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "kakao": {
        "APP": {
            "client_id": KAKAO_CLIENT_ID,
            "secret": KAKAO_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "profile_nickname",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "naver": {
        "APP": {
            "client_id": NAVER_CLIENT_ID,
            "secret": NAVER_CLIENT_SECRET,
            "key": "",
        },
        "SCOPE": [
            "name",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
}


LOGIN_REDIRECT_URL = "/"  # 로그인 성공 후 이동할 URL
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # 로그아웃 후 이동할 URL

# 이메일 필수 설정 (이메일 인증 요구)
ACCOUNT_EMAIL_VERIFICATION = "optional"  # (optional, mandatory, none)
ACCOUNT_EMAIL_REQUIRED = True

# 소셜 계정 이메일 검증 비활성화
SOCIALACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = False

# 로그인 시 사용자 이름 대신 이메일 사용
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_USERNAME_REQUIRED = False

# 자동 가입 활성화 (True 시 /accounts/signup/ 없이 자동 가입)
SOCIALACCOUNT_AUTO_SIGNUP = True

# 유저명 중복 방지
ACCOUNT_UNIQUE_EMAIL = True
