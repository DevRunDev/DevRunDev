from pathlib import Path

import environ

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
    "reviews",
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
                "enrollments.context_processors.cart_count",
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
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


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

# 수정된 코드 - 필요한 소셜 로그인만 활성화
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("Warning: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are not set. Google login will be disabled.")

if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    print("Warning: NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are not set. Naver login will be disabled.")

if not KAKAO_CLIENT_ID or not KAKAO_CLIENT_SECRET:
    print("Warning: KAKAO_CLIENT_ID and KAKAO_CLIENT_SECRET are not set. Kakao login will be disabled.")

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
ACCOUNT_SIGNUP_REDIRECT_URL = 'account_login'

SOCIALACCOUNT_LOGIN_ON_GET = True  # 소셜 로그인 중간 페이지 건너뛰기

# allauth 관련 설정 추가/수정
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True

# 템플릿 오버라이드를 위한 추가 설정
ACCOUNT_TEMPLATE_EXTENSION = "html"

# 회원가입 후 자동 로그인 설정
ACCOUNT_SESSION_REMEMBER = True  # 세션 유지
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True  # 회원가입 시 비밀번호 두 번 입력
ACCOUNT_USERNAME_REQUIRED = True  # 사용자 이름 필수
ACCOUNT_AUTHENTICATION_METHOD = "email"  # 이메일로 로그인
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # 이메일 확인 시 자동 로그인

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

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
