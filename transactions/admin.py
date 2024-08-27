from django.contrib import admin
from .models import Transactions, SendModel
from .views import transaction_mail_send
# Register your models here.
admin.site.register(SendModel)
@admin.register(Transactions)
class TransactionAdmin(admin.ModelAdmin):
    list_display= ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']

    def save_model(self, request, obj, form, change):
        if obj.loan_approve:
            obj.account.balance+=obj.amount
            obj.balance_after_transaction= obj.account.balance
            obj.account.save()
            transaction_mail_send(obj.account.user, obj.amount, 'Loan Approval', 'transactions/admin_loan_approve.html')
        return super().save_model(request, obj, form, change)
