from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import ProductReview,UserAddressBook

class SignupForm(UserCreationForm):
	class Meta:
		model=User
		fields=('first_name','last_name','email','username','password1','password2')

# Review Add Form
class ReviewAdd(forms.ModelForm):
	class Meta:
		model=ProductReview
		fields=('review_text','review_rating')

# AddressBook Add Form
class AddressBookForm(forms.ModelForm):
	class Meta:
		model=UserAddressBook
		fields=('address','mobile','status')

# ProfileEdit
class ProfileForm(UserChangeForm):
	class Meta:
		model=User
		fields=('first_name','last_name','email','username')

#phone number form
from django import forms

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=15, required=True, label='Mpesa Phone Number')






