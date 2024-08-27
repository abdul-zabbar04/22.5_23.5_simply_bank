from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .constant import acType, genderType
from .models import UserAddress, UserBankAccount
class UserRegistrationForm(UserCreationForm):
    ac_type= forms.ChoiceField(choices=acType)
    birthday= forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender= forms.ChoiceField(choices=genderType)
    street_address= forms.CharField(max_length=100)
    city= forms.CharField(max_length=100)
    postal_code= forms.IntegerField()
    country= forms.CharField(max_length=100)
    class Meta:
        model= User
        fields= ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'ac_type', 'birthday', 'gender', 'street_address', 'city', 'postal_code', 'country'] # User model ar field gula dite hobe. baki gula na dileu hoi
    
    def save(self, commit= True):
        new_user= super().save(commit=False)
        if commit == True:
            new_user.save()
            # here, we retrived form data which are fillup by user
            ac_type= self.cleaned_data.get('ac_type')
            birthday= self.cleaned_data.get('birthday')
            gender= self.cleaned_data.get('gender')
            street_address= self.cleaned_data.get('street_address')
            city= self.cleaned_data.get('city')
            postal_code= self.cleaned_data.get('postal_code')
            country= self.cleaned_data.get('country')

            UserBankAccount.objects.create(
                # model_field= retrived form data 
                user= new_user,
                ac_type= ac_type,
                ac_no= 100000+new_user.id,
                birthday= birthday,
                gender= gender
            )

            UserAddress.objects.create(
                # model_field= retrived form data
                user= new_user,
                street_address= street_address,
                city= city,
                postal_code= postal_code,
                country= country
            )
        return new_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 '
                )
            })

class UserUpdateForm(forms.ModelForm):
    ac_type= forms.ChoiceField(choices=acType)
    birthday= forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender= forms.ChoiceField(choices=genderType)
    street_address= forms.CharField(max_length=100)
    city= forms.CharField(max_length=100)
    postal_code= forms.IntegerField()
    country= forms.CharField(max_length=100)
    
    class Meta:
        model= User
        fields= ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500 '
                )
            })
        if self.instance:
            try:    # jodi try ar vitor er code gula valid hoy tahole ai section run hobe and except ke ignore kore jabe
                user_ac_form_data= self.instance.account
                user_address_form_data= self.instance.address
            except: # try a error hole except run hobe and try ke ignore kore asbe
                user_ac_form_data= None
                user_address_form_data= None
            
            if user_ac_form_data and user_address_form_data:
                self.fields['ac_type'].initial= user_ac_form_data.ac_type
                self.fields['birthday'].initial= user_ac_form_data.birthday
                self.fields['gender'].initial= user_ac_form_data.gender
                self.fields['street_address'].initial= user_address_form_data.street_address
                self.fields['city'].initial= user_address_form_data.city
                self.fields['postal_code'].initial= user_address_form_data.postal_code
                self.fields['country'].initial= user_address_form_data.country
    def save(self, commit= True):
        current_user= super().save(commit=False)
        if commit:
            current_user.save()
            user_ac_form_data, created= UserBankAccount.objects.get_or_create(user= current_user)
            user_address_form_data, created= UserAddress.objects.get_or_create(user= current_user)

            user_ac_form_data.ac_type=self.cleaned_data['ac_type']
            user_ac_form_data.gender=self.cleaned_data['gender']
            user_ac_form_data.birthday=self.cleaned_data['birthday']
            user_ac_form_data.save()

            user_address_form_data.street_address= self.cleaned_data['street_address']
            user_address_form_data.city= self.cleaned_data['city']
            user_address_form_data.postal_code= self.cleaned_data['postal_code']
            user_address_form_data.country= self.cleaned_data['country']
            user_address_form_data.save()
        return current_user