from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositView.as_view(), name='depositPage'),
    path('withdraw/', views.WithdrawView.as_view(), name='withdrawPage'),
    path('loan_request/', views.LoanRequestView.as_view(), name='loanPage'),
    path('report/', views.TransactionReportView.as_view(), name='reportPage'),
    path('loan_list/', views.LoanListView.as_view(), name='loanListPage'),
    path('pay_loan/<int:loan_id>/', views.PayLoanView.as_view(), name='payLoanPage'),
    path('send/', views.SendMoneyView.as_view(), name='sendPage'),
]
