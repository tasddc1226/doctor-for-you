# 로컬 실행 환경 설정

1. 프로젝트 클론을 받아주세요.

    ```bash
    ❯ git clone https://github.com/tasddc1226/doctor-for-you.git
    ```

2. 클론된 프로젝트로 이동합니다.

    ```bash
    ❯ cd doctor-for-you
    ```

3. venv를 이용한 가상환경을 생성 & 활성화 합니다.

    ```bash
    ❯ python3 -m venv venv
    ❯ source 프로젝트경로/doctor-for-you/venv/bin/activate
    ```

4. 아래의 명령어로 가상환경에 의존성 설치를 진행합니다.

    ```bash
    ❯ pip install -r requirements.txt
    ```

5. Database(sqlite3) migration을 진행합니다.

    ```bash
    ❯ python manage.py makemigrations
    ❯ python manage.py migrate
    ```

6. 데이터를 추가하기 위해 아래의 명령으로 슈퍼유저 생성을 진행합니다.

    ```bash
    ❯ python manage.py createsuperuser
    ```

7. 서버를 동작시키고 `localhost:8000/admin` 경로로 진입 후 생성한 슈퍼유저로 로그인합니다.

    ```bash
    ❯ python manage.py runserver
    ```

8. 의사, 환자 및 의사의 평일 혹은 주말에 대한 데이터를 임의로 추가합니다.

- 의사의 진료과 같은 경우 아래와 같이 콤마(,)로 연결하여 데이터를 추가할 수 있습니다.

- 의사의 비급여진료과목은 없을 수 있습니다.

    <img width="560" alt="Screen Shot 2022-07-22 at 14 46 51" src="https://user-images.githubusercontent.com/55699007/180371494-3415eef5-3340-4b56-ae98-bf5a5b7227c2.png">

- 의사의 평일 영업시간에 대한 데이터를 추가합니다.

    <img width="433" alt="Screen Shot 2022-07-22 at 14 53 17" src="https://user-images.githubusercontent.com/55699007/180372432-b6f06274-66fa-4079-860c-21c2de69e700.png">

- 의사의 주말 영업시간에 대한 데이터를 추가합니다.

    - 휴일 유무를 체크시 해당 요일은 휴무일 입니다.

        <img width="465" alt="Screen Shot 2022-07-22 at 14 56 43" src="https://user-images.githubusercontent.com/55699007/180372891-d12a2d66-9b58-4635-b29c-a796d2e82fd3.png">

</br>


# DB Diagram
![doctor-for-you](https://user-images.githubusercontent.com/55699007/180158413-87a24e15-8e70-428a-9459-e28fcf338afe.png)

</br>

# API Documentation

</br>

## 조건에 맞는 의사를 검색
- `GET` `/api/v1/search/?dept=일반의`

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "손웅래"
        },
        {
            "name": "선재원"
        }
    ]
    ```

- `GET` `/api/v1/search/?hospital=메라키`

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "손웅래"
        },
        {
            "name": "선재원"
        }
    ]
    ```

- `GET` `/api/v1/search/?hospital=메라키&doctor=손웅래`

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "손웅래"
        }
    ]
    ```

- `GET` `/api/v1/search/?dept=한의학과&doctor=선재원`

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "선재원"
        }
    ]
    ```

- `GET` `/api/v1/search/?doctor=손웅래&non_paid=다이어트`

- `Server Response`
    ```json
    // status: 200
    []
    ```

</br>


## 입력 시각에 영업중인 의사 검색
- `POST` `/api/v1/search/`

- `Request Body`
    ```json
    {
        "year": 2022,
        "month": 7,
        "day": 21,
        "hour": 15,
        "min" : 30
    }
    ```

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "손웅래"
        },
        {
            "name": "선재원"
        }
    ]
    ```

- `Request Body`
    ```json
    {
        "year": 2022,
        "month": 7,
        "day": 23,
        "hour": 9,
        "min" : 30
    }

- `Server Response`
    ```json
    // status: 200
    [
        {
            "name": "선재원"
        }
    ]
    ```

</br>

## 새로운 진료 예약 생성
- `POST` `/api/v1/cares/`

- `Request Body`
    ```json
    {
        "patient_id" : 1,
        "doctor_id" : 1,
        "year": 2022,
        "month": 7,
        "day": 22,
        "hour": 16,
        "min": 10
    }
    ```

- `Server Response`
    ```json
    // status: 201
    {
        "id": 20,
        "doctor_name": "손웅래",
        "patient_name": "김환자",
        "book_time": "2022-07-22T16:10:00",
        "created_at": "2022-07-21T17:27:29.642660",
        "expire_time": "2022-07-21T17:47:29.632890",
        "is_booked": false,
        "patient": 1,
        "doctor": 1
    }
    ```

### 예약 불가한 경우 1
- **예약 날짜가 현 시점보다 이전일 경우**

- `Request Body`
    ```json
    {
        "patient_id" : 1,
        "doctor_id" : 1,
        "year": 2022,
        "month": 7,
        "day": 20,
        "hour": 16,
        "min": 10
    }
    ```

- `Server Response`
    ```json
    // status: 400
    {
        "message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."
    }
    ```

### 예약 불가한 경우 2
- **희망 진료 시각에 의사가 진료(영업)를 하지 않는 경우**

- `Request Body`
    ```json
    {
        "patient_id" : 1,
        "doctor_id" : 1,
        "year": 2022,
        "month": 7,
        "day": 21,
        "hour": 21,
        "min": 10
    }
    ```

- `Server Response`
    ```json
    // status: 400
    {
        "message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."
    }
    ```

</br>

## 진료 요청 리스트 조회
- `GET` `/api/v1/cares/?id=1`

- `Server Response`

    ```json
    // status: 200
    [
        {
            "id": 16,
            "patient_name": "박환자",
            "book_time": "2022-07-21T13:45:00",
            "expire_time": "2022-07-21T13:25:39.545884"
        },
        {
            "id": 20,
            "patient_name": "김환자",
            "book_time": "2022-07-22T16:10:00",
            "expire_time": "2022-07-21T17:47:29.632890"
        }
    ]
    ```

</br>

## 진료 요청 수락
- `PATCH` `/api/v1/cares/20`

- `Server Response`

    ```json
    // status: 200
    {
        "id": 20,
        "doctor_name": "손웅래",
        "patient_name": "김환자",
        "book_time": "2022-07-22T16:10:00",
        "created_at": "2022-07-21T17:27:29.642660",
        "expire_time": "2022-07-21T17:47:29.632890",
        "is_booked": true,
        "patient": 1,
        "doctor": 1
    }
    ```

### 진료 요청 수락이 불가한 경우
- **expire_time이 만료된 경우**
- 또는 **이미 요청이 수락이 된 경우**

- `Server Response`

    ```json
    // status: 400
    {
        "message": "존재하지 않거나 이미 수락된 예약입니다."
    }
    ```
