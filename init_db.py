import pyodbc
import os
import sys

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
            print(f"✅ База данных '{db_name}' уже существует.")
        else:
            print(f"🔄 Создаю базу данных '{db_name}'...")
            cursor.execute(f"CREATE DATABASE [{db_name}]")
            print(f"✅ База данных '{db_name}' создана успешно.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Ошибка при подключении к базе данных: {e}")
        print("\n💡 Возможные причины:")
        print("   - Неправильные учетные данные (логин/пароль)")
        print("   - Сервер недоступен")
        print("   - Нет прав на создание базы данных")
        print("   - ODBC драйвер не установлен или указан неправильно")
        print("\n📋 Проверь переменные в .env:")
        print(f"   MS_SQL_SERVER = {os.getenv('MS_SQL_SERVER')}")
        print(f"   MS_SQL_LOGIN = {os.getenv('MS_SQL_LOGIN')}")
        print(f"   MS_SQL_DB = {os.getenv('MS_SQL_DB')}")
        print(f"   MS_SQL_DRIVER = {os.getenv('MS_SQL_DRIVER')}")
        print("\n📋 Установленные ODBC драйверы:")
        try:
            import pyodbc
            drivers = pyodbc.drivers()
            for driver in drivers:
                print(f"   - {driver}")
        except Exception as driver_err:
            print(f"   ❌ Не удалось получить список драйверов: {driver_err}")
        sys.exit(1)

if __name__ == "__main__":
    create_database_if_not_exists()