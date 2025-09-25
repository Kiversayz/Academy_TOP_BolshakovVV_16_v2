import pyodbc
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def update_env_var(key, value):
    """Обновляет или добавляет переменную в .env файл"""
    env_path = BASE_DIR / '.env'
    env_lines = []

    # Читаем текущий .env
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()

    # Ищем строку с ключом
    found = False
    for i, line in enumerate(env_lines):
        if line.startswith(key + '='):
            env_lines[i] = f"{key}={value}\n"
            found = True
            break

    # Если не нашли — добавляем в конец
    if not found:
        env_lines.append(f"{key}={value}\n")

    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(env_lines)

def create_database_if_not_exists():
    # Подключаемся к системной базе данных (master)
    master_conn_str = (
        f"DRIVER={os.getenv('MS_SQL_DRIVER', 'ODBC Driver 18 for SQL Server')};"
        f"SERVER={os.getenv('MS_SQL_SERVER')};"
        f"UID={os.getenv('MS_SQL_LOGIN')};"
        f"PWD={os.getenv('MS_SQL_PASS')};"
        "DATABASE=master;"
        "TrustServerCertificate=yes;"
    )

    try:
        conn = pyodbc.connect(master_conn_str)
        cursor = conn.cursor()

        db_name = os.getenv('MS_SQL_DB', 'AcademyTop')

        # Проверяем, существует ли БД
        cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{db_name}'")
        if cursor.fetchone():
            print(f"[+] Database '{db_name}' already exists.")
            update_env_var('USE_SQLITE', 'false')
        else:
            print(f"[>] Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE [{db_name}]")
            print(f"[+] Database '{db_name}' created successfully.")
            update_env_var('USE_SQLITE', 'false')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[X] Error connecting to SQL Server: {e}")
        print("\nPossible reasons:")
        print("   - Invalid credentials (login/password)")
        print("   - Server is unavailable")
        print("   - No rights to create database")
        print("   - ODBC driver not installed or incorrect")
        print("\nCheck variables in .env:")
        print(f"   MS_SQL_SERVER = {os.getenv('MS_SQL_SERVER')}")
        print(f"   MS_SQL_LOGIN = {os.getenv('MS_SQL_LOGIN')}")
        print(f"   MS_SQL_DB = {os.getenv('MS_SQL_DB')}")
        print(f"   MS_SQL_DRIVER = {os.getenv('MS_SQL_DRIVER')}")
        print("\nInstalled ODBC drivers:")
        try:
            drivers = pyodbc.drivers()
            for driver in drivers:
                print(f"   - {driver}")
        except Exception as driver_err:
            print(f"   [X] Failed to get driver list: {driver_err}")

        # Спрашиваем, использовать ли SQLite
        print("\n[?] Could not connect to SQL Server. Use SQLite instead? (y/n)")
        choice = input().strip().lower()

        if choice in ['y', 'yes', 'да', 'д']:
            print("[+] Using SQLite.")
            update_env_var('USE_SQLITE', 'true')
            # Создаём файл базы данных, если его нет
            db_path = BASE_DIR / 'db.sqlite3'
            if not db_path.exists():
                print(f"File '{db_path}' will be created during migration.")
            else:
                print(f"File '{db_path}' already exists.")
        else:
            print("[X] Connection to SQL Server failed, and SQLite not selected.")
            update_env_var('USE_SQLITE', 'false')
            sys.exit(1)

if __name__ == "__main__":
    create_database_if_not_exists()