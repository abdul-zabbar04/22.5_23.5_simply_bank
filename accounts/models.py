from django.db import models
from django.contrib.auth.models import User
from .constant import acType, genderType
# Create your models here.

class UserBankAccount(models.Model):
    user= models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    ac_type= models.CharField(max_length=10, choices=acType)
    ac_no= models.IntegerField(unique=True)
    birthday= models.DateField(null=True, blank=True)
    gender= models.CharField(max_length=10, choices=genderType)
    initial_deposite_date= models.DateField(auto_now_add=True)
    balance= models.DecimalField(default=0, max_digits=12, decimal_places=2)
    def __str__(self) -> str:
        return f'{self.user.username}-{self.ac_no}'

class UserAddress(models.Model):
    user= models.OneToOneField(User, related_name='address',on_delete=models.CASCADE)
    street_address= models.CharField(max_length=100)
    city= models.CharField(max_length=100)
    postal_code= models.IntegerField()
    country= models.CharField(max_length=100)
    def __str__(self) -> str:
        return f'{self.user.username}-{self.user.account.ac_no}'