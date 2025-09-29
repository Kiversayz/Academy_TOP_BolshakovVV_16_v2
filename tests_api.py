import requests

# Получаем токен через API
auth_response = requests.post("http://127.0.0.1:8000/api/auth/token/", json={
    "username": "testuser",
    "password": "ys6-xRK-6y6-H8y"
})

token = auth_response.json()['access']
print(token)


