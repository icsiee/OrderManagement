from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['username', 'password', 'email', 'budget']

    def save(self, commit=True):
        customer = super().save(commit=False)
        # Diğer işlem ve doğrulamalar burada yapılabilir
        if commit:
            customer.save()
        return customer
