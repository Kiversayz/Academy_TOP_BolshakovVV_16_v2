import pytest
from django.utils import timezone
from nursery.models import Pet
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_pet_get_age_in_months():
    user = User.objects.create_user(username='testuser', password='12345')
    birth_date = timezone.now().date().replace(month=timezone.now().date().month - 6)
    pet = Pet.objects.create(
        owner=user,
        name='Барсик',
        breed='Сиамская',
        animal_type='cat',
        birth_date=birth_date,
        price=1000.00,  # ← Добавь это
        currency='RUB'   # ← И это
    )
    assert pet.get_age_in_months() == 6
