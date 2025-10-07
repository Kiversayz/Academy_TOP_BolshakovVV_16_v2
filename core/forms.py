from django import forms
from .models import PetComment

class PetCommentForm(forms.ModelForm):
    class Meta:
        model = PetComment
        fields = ['content'] # Только текст комментария, pet и author будут установлены в view
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Напишите ваш комментарий...'}),
        }