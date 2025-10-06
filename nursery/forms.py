from django import forms
from .models import Pet, Pedigree

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields =[
            'name',
            'animal_type',
            'breed',
            'family',
            'birth_date',
            'price',
            'currency',
            'hypoallergenic',
            'feeding_type',
            'description',
            'image',
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Можно настроить поля формы здесь
        # Например, сделать какие-то обязательными/опциональными
        # self.fields['feeding_type'].required = False


class PedigreeForm(forms.ModelForm):
    class Meta:
        model = Pedigree
        fields = ['mother', 'father', 'generation', 'breeding_date', 'notes']