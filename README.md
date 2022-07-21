
# DB Diagram
![doctor-for-you](https://user-images.githubusercontent.com/55699007/180158413-87a24e15-8e70-428a-9459-e28fcf338afe.png)

# API Documentation
## 조건에 맞는 의사를 검색
- `GET` `/api/v1/search/?dept=일반의`

- `Server Response`
    ```json
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
    [
        {
            "name": "손웅래"
        }
    ]
    ```

- `GET` `/api/v1/search/?dept=한의학과&doctor=선재원`

- `Server Response`
    ```json
    [
        {
            "name": "선재원"
        }
    ]
    ```

- `GET` `/api/v1/search/?doctor=손웅래&non_paid=다이어트`

- `Server Response`
    ```json
    []
    ```

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
    [
        {
            "name": "선재원"
        }
    ]
    ```

## 새로운 진료 예약 생성
- `POST` `/api/v1/care/`

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
    {
        "message": "진료 예약이 불가능합니다. 다른 시간을 선택해주세요."
    }
    ```


## 진료 요청 리스트 조회
- `GET` `/api/v1/care/?id=1`

- `Server Response`

    ```json
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

## 진료 요청 수락
- `PATCH` `/api/v1/care/20`

- `Server Response`

    ```json
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
    {
        "message": "존재하지 않거나 이미 수락된 예약입니다."
    }
    ```
