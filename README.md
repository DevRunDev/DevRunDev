# DevRunDev
- DevRunDev는 IT 및 개발자를 위한 온라인 교육 플랫폼입니다.
- 강사들은 실무 중심의 강의를 제작하고 수강생들은 최신 기술을 배우며 성장할 수 있도록 지원합니다.
- 또한 강의 진행률, 평가 시스템, 강의 별 퀴즈 등의 기능을 통해 효율적인 학습 경험을 제공합니다.

## 1. 🎯 주요 기능
### 1) 사용자 관리

- 역할 기반 사용자 시스템: 학생, 강사, 관리자 역할 구분
- 소셜 로그인: Google, Kakao, Naver 로그인 지원
- 강사 신청: 강사 자격 신청 및 관리자 승인 기능

### 2) 강의 관리

- 섹션 및 레슨 구조: 체계적인 강의 구조 제공
- 강의 승인 프로세스: 품질 관리를 위한 강의 승인 워크플로우
- 강의 검색 및 필터링: 사용자 친화적인 강의 탐색 기능
- 강의 수정 및 관리: 강사가 직접 강의 콘텐츠 관리

### 3) 학습 기능

- 강의 진행률 추적: 학습 현황 및 진행률 확인
- 퀴즈 및 평가: 학습 이해도 확인을 위한 퀴즈 시스템
- 수료증 발급: 강의 완료 시 수료증 발급 기능
- 강의 리뷰 및 평가: 강의 품질을 위한 리뷰 시스템

### 4) 수강 관리

- 장바구니 기능: 여러 강의 동시 수강 신청
- 수강 신청 관리: 수강 현황 및 관리 대시보드

## 2. 🛠️ 기술 스택

### 1) Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![precommit](https://img.shields.io/badge/precommit-FAB040?style=for-the-badge&logo=precommit&logoColor=white)
![githubactions](https://img.shields.io/badge/githubactions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

### 2) 백엔드

![Django](https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white)

Django 주요 패키지:

django-allauth: 소셜 로그인 지원 (Google, Kakao, Naver)

django-environ: 환경 변수 관리

django-extensions: 개발 유틸리티

django-debug-toolbar: 개발 디버깅 도구

Authentication: Django Authentication + django-allauth

### 3) Database
![SQLite3](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=SQLite&logoColor=white)

### 4) 프론트엔드

![Bootstrap](https://img.shields.io/badge/bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML](https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white)



## 3. 🌐 개발 환경 세팅

### git clone
```sh
git clone git@github.com:DevRunDev/DevRunDev.git
```

### 가상 환경 설정 및 패키지 설치
```sh
cd DevRunDev
python -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### .env
```sh
cp env.dev.example .env

# .env에 필요한 설정 추가
```

### pre-commit hook

git clone 후 아래 명령어 실행 필요
```sh
pre-commit install
```

### migration
```sh
python manage.py migrate
```

### seed_data command

```sh
python manage.py seed_data
```

## 4.📝 API 문서
### 1) 사용자 관리 API

#### 로그인 및 인증

| 메서드 | URL패턴 | 기능 | 로그인 권한 필요 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|:-:|
|POST | /accounts/login/ | 사용자 로그인 |
|POST | /accounts/logout/ | 사용자 로그아웃 | ✅ | |
|GET | /accounts/profile/ | 사용자 프로필 조회 | ✅ | |
|POST | /accounts/instructor/apply/ | 강사 신청 | ✅ | ✅ |

### 2) 강의 관리 API

#### 강의 목록 및 상세

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|GET | / | 강의 목록 조회 | ✅ | |
|GET | /courses/{id}/ | 강의 상세 조회 | ✅ | |
|GET | /courses/lessons/{id}/ | 레슨 상세 조회 | ✅ | |

#### 강의 생성 및 관리

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|GET,POST | /courses/create/step1/ | 강의 생성 1단계 (기본 정보) | | ✅ |
|GET,POST | /courses/create/step2/ | 강의 생성 2단계 (섹션 구성) | | ✅ |
|GET,POST | /courses/create/step3/ | 강의 생성 3단계 (레슨 추가) | | ✅ |
|GET,POST | /courses/create/step4/ | 강의 생성 4단계 (퀴즈 추가 및 강의 정보 검토) | | ✅ |
|GET | /courses/review/ | 강의 심사 대기 페이지 | | ✅ |
|GET | /courses/instructor/dashboard/ | 강사 대시보드 | | ✅ |
|GET,POST | /courses/{id}/edit/ | 강의 수정 | | ✅ |
|POST | /courses/sections/{id}/add/ | 섹션 추가 | | ✅ |
|POST | /courses/sections/{id}/edit/ | 섹션 수정 | | ✅ |
|POST | /courses/sections/{id}/delete/ | 섹션 삭제 | | ✅ |
|POST | /courses/lessons/{id}/add/ | 레슨 추가 | | ✅ |
|POST | /courses/lessons/{id}/edit/ | 레슨 수정 | | ✅ |
|POST | /courses/lessons/{id}/delete/ | 레슨 삭제 | | ✅ |

### 3) 수강 관리 API

#### 수강 신청 및 관리

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|POST | /enrollments/enroll/{course_id}/ | 강의 수강 신청 | ✅ | |
|GET | /enrollments/enroll/{course_id}/success/ | 수강 신청 성공 페이지 | ✅ | |
|POST | /enrollments/lesson/{lesson_id}/complete/ | 레슨 완료 처리 | ✅ | |
|GET | /enrollments/dashboard/ | 학생 대시보드 | ✅ | |
|GET | /enrollments/ | 수강 중인 강의 목록 | ✅ | |
|GET | /enrollments/{id}/ | 수강 상세 정보 | ✅ | |
|GET | /enrollments/{id}/generate-certificate/ | 수료증 발급 | ✅ | |
|GET | /enrollments/certificate/{id}/ | 수료증 조회 | ✅ | |
|GET | /enrollments/certificate/{id}/download/ | 수료증 다운로드 | ✅ | |

#### 장바구니 기능

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|GET | /enrollments/cart/ | 장바구니 조회 | ✅ | |
|POST | /enrollments/cart/add/{course_id}/ | 장바구니 추가 | ✅ | |
|POST | /enrollments/cart/enroll/ | 장바구니에서 수강 신청 | ✅ | |
|POST | /enrollments/cart/remove/{course_id}/ | 장바구니에서 제거 | ✅ | |

### 4) 퀴즈 API

#### 퀴즈 관리

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|GET | /quizzes/course/{course_id}/quizzes/ | 퀴즈 목록 | | ✅ |
|POST | /quizzes/course/{course_id}/quizzes/create/ | 퀴즈 생성  | | ✅ |
|GET | /quizzes/{id}/ | 퀴즈 상세 | | ✅ |
|POST | /quizzes/{id}/edit/ | 퀴즈 수정 | | ✅ |
|POST | /quizzes/{id}/delete/ | 퀴즈 삭제 | | ✅ |

#### 문제 관리

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|POST | /quizzes/quizzes/{quiz_id}/questions/create/ | 문제 생성 | | ✅ |
|POST | /quizzes/questions/{id}/edit/ | 문제 수정 | | ✅ |
|POST | /quizzes/questions/{id}/delete/ | 문제 삭제 | | ✅ |

#### 퀴즈 응시

| 메서드 | URL패턴 | 기능 | 학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|POST | /quizzes/quizzes/{id}/take/ | 퀴즈 응시 | ✅ | |
|GET | /quizzes/attempts/{id}/result/ | 퀴즈 결과 조회 | ✅ | |

### 5) 리뷰 API

| 메서드 | URL패턴 | 기능 |학생 권한 필요 | 강사 권한 필요 |
|:-|:-|:-|:-:|:-:|
|POST | /reviews/course/{course_id}/add/ | 리뷰 작성 | ✅ | |
|POST | /reviews/review/{review_id}/edit/ | 리뷰 수정 |✅ | |
|POST | /reviews/review/{review_id}/delete/ | 리뷰 삭제 |✅ | |


## 5. 📁프로젝트 구조
```
📁DevRunDev/
├── 📁 .github/workflows/      # GitHub CI/CD 워크플로우
│   └── pr_ci.yml              # PR 시 테스트 자동화
├── 📁 accounts/               # 사용자 관리
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── tests/
│   ├── urls.py
│   └── views.py
├── 📁 courses/                # 강의 관리
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── templates/
│   ├── tests/
│   ├── urls.py
│   └── views.py
├── 📁 enrollments/            # 수강 신청 및 관리
│   ├── admin.py
│   ├── models.py
│   ├── templates/
│   ├── urls.py
│   └── views.py
├── 📁 quizzes/                # 퀴즈 관리
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── templates/
│   ├── tests/
│   ├── urls.py
│   └── views.py
├── 📁 reviews/                # 리뷰 관리
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── 📁 core/                   # 공통 기능
│   └── management/
│       └── commands/
│           └── seed_data.py   # 샘플 데이터 생성
├── 📁 config/                 # 프로젝트 설정
│   ├── settings.py            # 기본 설정 파일
│   ├── urls.py                # 메인 URL 설정
│   └── wsgi.py                # WSGI 설정
├── 📁 static/                 # 정적 파일
│   ├── css/
│   ├── js/
│   └── images/
├── 📁 templates/              # 공통 템플릿
│   ├── account/               # 계정 관련 템플릿
│   └── base.html              # 기본 템플릿
├── 📁 media/                  # 업로드 파일 저장
├── 📁 docs/                   # 프로젝트 문서
├── 📄 .env.dev.example        # 환경 변수 예시
├── 📄 .gitignore
├── 📄 .pre-commit-config.yaml # pre-commit 설정
├── 📄 manage.py               # Django 관리 명령어
├── 📄 pytest.ini              # pytest 설정
└── 📄 requirements.txt        # 의존성 패키지
```

## 6. 화면 설계
1) Google Social Login
![Google Login](https://github.com/user-attachments/assets/7a151eff-1ff3-4862-b13e-7d4f6927ff3d)

2) Kakao Social Login
![Kakao Login](https://github.com/user-attachments/assets/2bb2f899-21b6-4c32-9ffe-32c7e146e55b)

3) Naver Social Login
![Naver Login](https://github.com/user-attachments/assets/b3df8b03-065f-4a29-8243-44fa85af75fb)

4) 회원가입
![signup](https://github.com/user-attachments/assets/4108cbf7-6226-43c6-87f5-4ec34ca5d4c0)

5) 강사 신청
![강사 신청](https://github.com/user-attachments/assets/703489c8-f76a-442a-8e94-dcb14c72941e)

6) 강의 생성
![강의 생성](https://github.com/user-attachments/assets/76148a2b-8cfd-4758-9b6b-9935e632aefd)

7) 강의 및 섹션 수정
![강의 및 섹션 수정](https://github.com/user-attachments/assets/5718fe3e-b8cf-4192-a1aa-2740b3c8bd5a)

8) 장바구니 담기 및 수강 신청
![장바구니 담기 및 수강 신청](https://github.com/user-attachments/assets/04660b1a-4f3a-469d-9e63-964b90656ec0)

9) 강의 상세 페이지
<img width="1280" alt="강의 상세 페이지" src="https://github.com/user-attachments/assets/70800157-0ecc-47cc-8d0d-0a576315bde8" />

10) 퀴즈 응시
![퀴즈 응시](https://github.com/user-attachments/assets/0b7a6027-edef-4b7c-8a87-a0a8c654b9ce)

11) 수료증 발급
![수료증 발급](https://github.com/user-attachments/assets/52eb8d29-f8df-42e1-bf19-e6bc1d3b080d)

12) 리뷰 작성
![리뷰 작성](https://github.com/user-attachments/assets/e043673e-a678-4479-b2ed-3e9bce57156c)


## 7. 데이터베이스 모델링(ERD)

![devrundev_erd](https://github.com/user-attachments/assets/3e15deb4-62c1-4198-8fd0-d9f7b8cf56be)


## 8. Architecture

![DevRunDev_mermaid-diagram](https://github.com/user-attachments/assets/15a95f8f-5c60-49ce-8699-ed6b8b5531c4)
