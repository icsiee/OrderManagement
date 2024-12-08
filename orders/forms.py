from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

class RegisterForm(forms.ModelForm):
    # customer_name alanını ekliyoruz
    customer_name = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    budget = forms.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Customer
        fields = ['customer_name', 'password', 'budget']

    def clean_customer_name(self):
        customer_name = self.cleaned_data.get('customer_name')
        if Customer.objects.filter(customer_name=customer_name).exists():
            raise forms.ValidationError('Bu kullanıcı adı zaten alınmış.')
        return customer_name

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget < 500 or budget > 3000:
            raise forms.ValidationError('Bütçe 500 ile 3000 TL arasında olmalıdır.')
        return budget

    def save(self, commit=True):
        # Şifreyi güvenli bir şekilde hashlemek
        customer = super().save(commit=False)
        customer.set_password(self.cleaned_data['password'])
        if commit:
            customer.save()
        return customer
