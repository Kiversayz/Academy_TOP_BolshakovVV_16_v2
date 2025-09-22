import pyodbc

# Попробуем получить список доступных драйверов
print("Доступные драйверы:")
for driver in pyodbc.drivers():
    print(driver)

# Проверим, есть ли нужный драйвер
target_driver = "ODBC Driver 17 for SQL Server"
if target_driver in pyodbc.drivers():
    print(f"\n✅ Драйвер '{target_driver}' найден!")
else:
    print(f"\n❌ Драйвер '{target_driver}' НЕ найден в системе!")