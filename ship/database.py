# database.py
# SQLite 데이터베이스 생성, 저장, 조회, 삭제 기능을 담당하는 파일

import os
import sqlite3
from datetime import datetime

import pandas as pd


# ──────────────────────────────────────────
# 데이터베이스 파일 경로 설정
# ──────────────────────────────────────────
DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "ship_fuel.db")


def create_database():
    """
    데이터베이스와 fuel_records 테이블을 생성하는 함수.
    data 폴더가 없으면 자동으로 생성합니다.
    """
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS fuel_records (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            ship_name        TEXT    NOT NULL,
            distance         REAL    NOT NULL,
            speed            REAL    NOT NULL,
            operation_hours  REAL    NOT NULL,
            fuel_per_hour    REAL    NOT NULL,
            fuel_price       REAL    NOT NULL,
            total_fuel       REAL    NOT NULL,
            total_cost       REAL    NOT NULL,
            created_at       TEXT    NOT NULL
        )
    """

    cursor.execute(create_table_sql)
    connection.commit()
    connection.close()


def save_record(
    ship_name: str,
    distance: float,
    speed: float,
    operation_hours: float,
    fuel_per_hour: float,
    fuel_price: float,
    total_fuel: float,
    total_cost: float
) -> bool:
    """
    계산 결과를 데이터베이스에 저장하는 함수.

    Returns:
        bool: 저장 성공 시 True, 실패 시 False
    """
    try:
        if not os.path.exists(DB_FOLDER):
            os.makedirs(DB_FOLDER)

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        insert_sql = """
            INSERT INTO fuel_records (
                ship_name,
                distance,
                speed,
                operation_hours,
                fuel_per_hour,
                fuel_price,
                total_fuel,
                total_cost,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            ship_name,
            distance,
            speed,
            operation_hours,
            fuel_per_hour,
            fuel_price,
            total_fuel,
            total_cost,
            created_at
        )

        cursor.execute(insert_sql, values)
        connection.commit()
        connection.close()

        return True

    except sqlite3.Error as e:
        print(f"DB 저장 오류: {e}")
        return False


def get_all_records() -> pd.DataFrame:
    """
    저장된 모든 운항 기록을 불러오는 함수.
    최신 기록이 위에 오도록 id 기준 내림차순 정렬합니다.

    Returns:
        pd.DataFrame: 저장 기록 데이터프레임
    """
    try:
        if not os.path.exists(DB_PATH):
            create_database()

        connection = sqlite3.connect(DB_PATH)

        select_sql = """
            SELECT
                id              AS 번호,
                ship_name       AS 선박명,
                distance        AS '운항거리(km)',
                speed           AS '평균속도(km/h)',
                operation_hours AS '운항시간(h)',
                fuel_per_hour   AS '시간당연료(L/h)',
                fuel_price      AS '연료단가(원/L)',
                total_fuel      AS '총연료(L)',
                total_cost      AS '총비용(원)',
                created_at      AS 저장일시
            FROM fuel_records
            ORDER BY id DESC
        """

        df = pd.read_sql_query(select_sql, connection)
        connection.close()

        return df

    except sqlite3.Error as e:
        print(f"DB 조회 오류: {e}")
        return pd.DataFrame()


def delete_record(record_id: int) -> bool:
    """
    특정 번호의 운항 기록을 삭제하는 함수.

    Args:
        record_id (int): 삭제할 기록 id

    Returns:
        bool: 삭제 성공 시 True, 실패 시 False
    """
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        delete_sql = "DELETE FROM fuel_records WHERE id = ?"
        cursor.execute(delete_sql, (record_id,))

        connection.commit()
        connection.close()

        return True

    except sqlite3.Error as e:
        print(f"DB 삭제 오류: {e}")
        return False


if __name__ == "__main__":
    create_database()

    success = save_record(
        ship_name="독도호",
        distance=1500.0,
        speed=25.0,
        operation_hours=60.0,
        fuel_per_hour=120.0,
        fuel_price=1800.0,
        total_fuel=7200.0,
        total_cost=12960000.0
    )

    if success:
        print("✅ 테스트 데이터 저장 성공")
    else:
        print("❌ 테스트 데이터 저장 실패")

    df = get_all_records()
    print(df.to_string(index=False))
