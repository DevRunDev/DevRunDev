# DevRunDev


## 주요 기능
### 사용자 관리

- 역할 기반 사용자 시스템: 학생, 강사, 관리자 역할 구분
- 소셜 로그인: Google, Kakao, Naver 로그인 지원
- 강사 신청: 강사 자격 신청 및 관리자 승인 기능

### 강의 관리

- 섹션 및 레슨 구조: 체계적인 강의 구조 제공
- 강의 승인 프로세스: 품질 관리를 위한 강의 승인 워크플로우
- 강의 검색 및 필터링: 사용자 친화적인 강의 탐색 기능
- 강의 수정 및 관리: 강사가 직접 강의 콘텐츠 관리

### 학습 기능

- 강의 진행률 추적: 학습 현황 및 진행률 확인
- 퀴즈 및 평가: 학습 이해도 확인을 위한 퀴즈 시스템
- 수료증 발급: 강의 완료 시 수료증 발급 기능
- 강의 리뷰 및 평가: 강의 품질을 위한 리뷰 시스템

### 결제 및 수강 관리

- 장바구니 기능: 여러 강의 동시 수강 신청
- 수강 신청 관리: 수강 현황 및 관리 대시보드

## 🛠️ 기술 스택

### Environment
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)   
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)   
![precommit](https://img.shields.io/badge/precommit-FAB040?style=for-the-badge&logo=precommit&logoColor=white) 
![githubactions](https://img.shields.io/badge/githubactions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white) 

### 백엔드

![Django](https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white)

Django 주요 패키지:

django-allauth: 소셜 로그인 지원 (Google, Kakao, Naver)

django-environ: 환경 변수 관리

django-extensions: 개발 유틸리티

django-debug-toolbar: 개발 디버깅 도구

Authentication: Django Authentication + django-allauth

### Database
![SQLite3](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=SQLite&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=white)

### 프론트엔드

![Bootstrap](https://img.shields.io/badge/bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML](https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white)



## 개발 환경 세팅

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

## API 문서
### 사용자 관리 API

#### 로그인 및 인증

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|POST | /accounts/login/ | 사용자 로그인|
|POST | /accounts/logout/ | 사용자 로그아웃|
|GET | /accounts/profile/ | 사용자 프로필 조회|
|POST | /accounts/instructor/apply/ | 강사 신청|


### 강의 관리 API
#### 강의 목록 및 상세

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|GET | / | 강의 목록 조회 |
|GET | /course/{id}/ | 강의 상세 조회 |
|GET | /lesson/{id}/ | 레슨 상세 조회 |

#### 강의 생성 및 관리

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|GET,POST | /create/step1/ | 강의 생성 1단계 (기본 정보)|
|GET,POST | /create/step2/ | 강의 생성 2단계 (섹션 구성)|
|GET,POST | /create/step3/ | 강의 생성 3단계 (레슨 추가)|
|GET,POST | /create/step4/ | 강의 생성 4단계 (퀴즈 추가)|
|GET | /instructor/dashboard/ | 강사 대시보드|
|GET,POST | /course/{id}/edit/ | 강의 수정|
|GET,POST | /sections/{id}/add/ | 섹션 추가|
|GET,POST | /sections/{id}/edit/ | 섹션 수정|
|GET | /sections/{id}/delete/ | 섹션 삭제|
|GET,POST | /lessons/{id}/add/ | 레슨 추가|
|GET,POST | /lessons/{id}/edit/ | 레슨 수정|
|GET | /lessons/{id}/delete/ | 레슨 삭제|

### 수강 관리 API
#### 수강 신청 및 관리

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|POST | /enrollments/enroll/{course_id}/ | 강의 수강 신청|
|POST | /enrollments/lesson/{lesson_id}/complete/ | 레슨 완료 처리|
|GET | /enrollments/dashboard/ | 학생 대시보드|
|GET | /enrollments/ | 수강 중인 강의 목록|
|GET | /enrollments/{id}/ | 수강 상세 정보|
|GET | /enrollments/{id}/generate-certificate/ | 수료증 발급|
|GET | /enrollments/certificate/{id}/ | 수료증 조회|
|GET | /enrollments/certificate/{id}/download/: 수료증 다운로드|

#### 장바구니 기능

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|GET | /enrollments/cart/ | 장바구니 조회|
|POST | /enrollments/cart/add/{course_id}/ | 장바구니 추가|
|POST | /enrollments/cart/enroll/ | 장바구니에서 수강 신청|
|POST | /enrollments/cart/remove/{course_id}/ | 장바구니에서 제거|

### 퀴즈 API
#### 퀴즈 관리

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|GET | /quizzes/course/{course_id}/quizzes/ | 퀴즈 목록
|GET,POST | /quizzes/course/{course_id}/quizzes/create/ | 퀴즈 생성
|GET | /quizzes/{id}/: 퀴즈 상세
|GET,POST | /quizzes/{id}/edit/ | 퀴즈 수정
|GET,POST | /quizzes/{id}/delete/ | 퀴즈 삭제

#### 문제 관리

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
| GET,POST | /quizzes/quizzes/{quiz_id}/questions/create/ | 문제 생성
| GET,POST | /quizzes/questions/{id}/edit/ | 문제 수정
| GET,POST | /quizzes/questions/{id}/delete/ | 문제 삭제

#### 퀴즈 응시

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
| GET,POST | /quizzes/quizzes/{id}/take/ | 퀴즈 응시 |
| GET | /quizzes/attempts/{id}/result/ | 퀴즈 결과 조회 |

### 리뷰 API

| 메서드 | URL패턴 | 기능 |
|--------|-----|-------------|
|POST | /reviews/course/{course_id}/add/ | 리뷰 작성 |
|POST | /reviews/review/{review_id}/edit/ | 리뷰 수정 |
|POST | /reviews/review/{review_id}/delete/ | 리뷰 삭제 |
