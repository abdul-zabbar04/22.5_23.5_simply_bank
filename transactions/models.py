from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTIONS_TYPE

# Create your models here.
class Transactions(models.Model):
    account= models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='transactions')
    amount= models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction= models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type= models.IntegerField(choices=TRANSACTIONS_TYPE, blank=True, null=True)
    timestamp= models.DateTimeField(auto_now_add=True)
    loan_approve= models.BooleanField(default=False)

    class Meta:
        ordering= ['-timestamp']

class SendModel(models.Model):
    ac_no= models.IntegerField()
    amount= models.DecimalField(max_digits=12, decimal_places=2)
    timestamp= models.DateField(auto_now_add=True)

    class Meta:
        ordering= ['-timestamp']

    

    
    
    