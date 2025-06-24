# 🔐 My Todo App - Backend

> Flask 기반의 경량 백엔드로, 사용자 인증 및 To-do 데이터를 관리합니다.  
> JWT 기반 인증을 사용하며, Vue 프론트엔드와 REST API로 연동됩니다.

---

## 🚀 기술 스택

- **Python 3.10+**
- **Flask**
- **Flask-JWT-Extended**
- **Flask-CORS**
- **SQLAlchemy (ORM)**
- **SQLite** 

---

## 📦 프로젝트 구조

```bash
backend/
├── app.py               # 앱 진입점, 회원가입, 로그인, 투두 관련 api 정의
├── models.py            # 데이터 모델 정의
└── requirements.txt  


```
---


## 🛠️ 설치 및 실행

### 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

### 의존성 설치
pip install -r requirements.txt

### 서버 실행
python app.py


---


## 🔐 JWT 인증

회원가입: POST /auth/register

로그인: POST /auth/login

모든 보호된 API는 Authorization: Bearer <JWT> 헤더 필요


---


## 주요 API 엔드포인트

| 메서드    | 경로               | 설명       |
| ------ | ---------------- | -------- |
| POST   | `/auth/register` | 회원가입     |
| POST   | `/auth/login`    | 로그인      |
| GET    | `/todos`         | 투두 목록 조회 |
| POST   | `/todos`         | 투두 추가    |
| PUT    | `/todos/<id>`    | 투두 수정    |
| DELETE | `/todos/<id>`    | 투두 삭제    |


---


## 외부 접근 주소 (JCLOUD를 통한 배포)

### 프론트엔드
http://113.198.66.75:13059

### 백엔드
http://113.198.66.75:10059


---
