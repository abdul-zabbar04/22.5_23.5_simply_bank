from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, FormView
from .models import Transactions, UserBankAccount, SendModel
from accounts.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import Deposit, Withdraw, LoanRequest, SendMoneyForm
from .constants import DEPOSIT, WITHDRAW, LOAN, LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


# Create your views here.
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    model= Transactions
    template_name= 'transactions/transaction_form.html'
    title= ''
    success_url= reverse_lazy('reportPage')

    def get_form_kwargs(self):
        kwargs= super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context.update({
            'title': self.title
        })
        return context
    
def transaction_mail_send(user, amount, subject, message_tem):
    message = render_to_string(message_tem, {
        'user': user,
        'amount': amount,
    })
    send_mail= EmailMultiAlternatives(subject, '', to=[user.email])
    send_mail.attach_alternative(message, 'text/html')
    send_mail.send()


class DepositView(TransactionCreateMixin):
    form_class= Deposit
    title= 'Deposit'

    def get_initial(self):
        initial= {'transaction_type': DEPOSIT}
        return initial
    def form_valid(self, form):
        amount= form.cleaned_data.get('amount')
        account= self.request.user.account
        account.balance+=amount
        account.save(
            update_fields= ['balance']
        )
        messages.success(self.request, f'{amount} BDT is deposited to your account successfully')
        transaction_mail_send(user= self.request.user, amount= amount, subject="Deposit", message_tem='transactions/deposit_mail.html')
        return super().form_valid(form)
    
class WithdrawView(TransactionCreateMixin):
    form_class= Withdraw
    title='Withdraw'

    def get_initial(self):
        initial= {'transaction_type':WITHDRAW}
        return initial
    def form_valid(self, form):
        total_deposite= Transactions.objects.filter(transaction_type= 1).aggregate(Sum('amount'))['amount__sum']
        total_withdraw= Transactions.objects.filter(transaction_type= 2).aggregate(Sum('amount'))['amount__sum']
        paid_loan= Transactions.objects.filter(transaction_type= 4).aggregate(Sum('amount'))['amount__sum']
        total_loan= Transactions.objects.filter(transaction_type= 3, loan_approve= True).aggregate(Sum('amount'))['amount__sum']
        if total_loan==None:
            total_loan=0
        if total_deposite==None:
            total_deposite=0
        if total_withdraw==None:
            total_withdraw=0
        if paid_loan==None:
            paid_loan=0
        total_outgoing= total_withdraw+total_loan
        total_incoming= total_deposite+paid_loan
        current_bank_balance=0
        if total_incoming>total_outgoing:
            current_bank_balance= total_incoming-total_outgoing
        account= self.request.user.account
        amount= form.cleaned_data.get('amount')
        if amount<=current_bank_balance:
            account.balance-=amount
            account.save(
                update_fields=['balance']
            )
            messages.success(self.request, f'{amount} BDT is withdrawn from your account successfully')
            transaction_mail_send(self.request.user, amount, 'Withdraw', 'transactions/withdraw_mail.html')
        else:
            messages.success(self.request, 'Sorry!Bank is bankrupted.')
        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class= LoanRequest
    title='Request For Loan'
    success_url= reverse_lazy('loanListPage')

    def get_initial(self):
        initial= {'transaction_type': LOAN}
        return initial
    def form_valid(self, form):
        account= self.request.user.account
        amount= form.cleaned_data.get('amount')
        current_loan_count= Transactions.objects.filter(account=self.request.user.account, transaction_type= 3, loan_approve= True).count()
        if current_loan_count>2:
            return HttpResponse('You are not eligible to get loan')
        messages.success(self.request, f'Loan request for amount {amount} BDT has been sent to admin')
        transaction_mail_send(self.request.user, amount, 'Loan Request', 'transactions/loan_req_mail.html')
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name= 'transactions/transaction_report.html'
    model= Transactions
    balance= 0

    def get_queryset(self):
        queryset= super().get_queryset().filter(
            account= self.request.user.account
        )
        start_date_str= self.request.GET.get('start_date')
        end_date_str= self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date= datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date= datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset= queryset.filter(timestamp__date__gte= start_date, timestamp__date__lte= end_date)
            self.balance= Transactions.objects.filter(timestamp__date__gte= start_date, timestamp__date__lte= end_date).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance= self.request.user.account.balance
        return queryset.distinct()
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['sends']= SendModel.objects.all()
        context.update({
            'account': self.request.user.account
        })
        return context

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan= get_object_or_404(Transactions, id= loan_id)
        
        if loan.loan_approve:
            user_ac= loan.account
            if loan.amount<user_ac.balance:
                user_ac.balance-=loan.amount
                loan.balance_after_transaction= user_ac.balance
                user_ac.save()
                loan.transaction_type= LOAN_PAID
                loan.save()
                transaction_mail_send(self.request.user, loan.amount, 'Pay Loan', 'transactions/pay_loan.html')
            else:
                messages.error(self.request, 'Insufficient Balance')
            return redirect('loanListPage')

class LoanListView(LoginRequiredMixin, ListView):
    model= Transactions
    template_name='transactions/loan_request.html'
    context_object_name= 'loans'
    title='Loan Report'

    def get_queryset(self):
        user_account= self.request.user.account
        queryset= Transactions.objects.filter(account= user_account, transaction_type= LOAN)
        return queryset

class SendMoneyView(FormView):
    form_class= SendMoneyForm
    template_name= 'transactions/send.html'
    success_url= reverse_lazy('reportPage')

    def form_valid(self, form):
        ac_no= form.cleaned_data.get('ac_no')
        amount= form.cleaned_data.get('amount')
        sender_ac= self.request.user.account
        try:
            receiver_ac= UserBankAccount.objects.get(ac_no=ac_no)
        except:
            receiver_ac= None
        if receiver_ac:
            if amount<=sender_ac.balance:
                form.save()
                sender_ac.balance-=amount
                receiver_ac.balance+=amount
                sender_ac.save()
                receiver_ac.save()
                messages.success(self.request, f'{amount}  BDT is sent to {receiver_ac.ac_no} successfully.')
                transaction_mail_send(self.request.user, amount, "Send Money", "transactions/send_mail.html")
                transaction_mail_send(receiver_ac.user, amount, "Receive Money", "transactions/receive_mail.html")
            else:
                messages.error(self.request, 'Insufficient Balance!')
        else:
            messages.error(self.request, "Not Founded this account number!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['title']='Send Money'
        return context
   


    
