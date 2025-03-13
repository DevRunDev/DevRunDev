# DevRunDev

## 개발 환경 세팅

### git clone
```sh
git clone git@github.com:DevRunDev/DevRunDev.git
```

### 가상 환경 설정 및 패키지 설치
```sh
co DevRunDev
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
