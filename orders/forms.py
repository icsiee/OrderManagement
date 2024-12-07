from django import forms
from .models import Customer

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'password', 'budget']
        widgets = {
            'password': forms.PasswordInput(),
            'budget': forms.NumberInput(attrs={'placeholder': '500-3000 TL arasında bir değer giriniz.'}),
        }

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get('customer_name')
        # Aynı isimle kullanıcı olup olmadığını kontrol et
        if Customer.objects.filter(customer_name=customer_name).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış.")
        return customer_name

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if not 500 <= budget <= 3000:
            raise forms.ValidationError("Bütçe 500 ile 3000 TL arasında olmalıdır.")
        return budget
