from django import forms
from django.core.exceptions import ValidationError
from .models import Customer
from django.contrib.auth.hashers import make_password


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, max_length=255)
    budget = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Customer
        fields = ['customer_name', 'password', 'budget']

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get('customer_name')
        if Customer.objects.filter(customer_name=customer_name).exists():
            raise ValidationError("Bu kullanıcı adı zaten mevcut.")
        return customer_name

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget < 500 or budget > 3000:
            raise ValidationError("Bütçe miktarı 500 ile 3000 TL arasında olmalıdır.")
        return budget

    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.password = make_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            customer.save()
        return customer
