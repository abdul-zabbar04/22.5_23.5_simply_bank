from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView, View
from .forms import UserRegistrationForm, UserUpdateForm
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from transactions.views import transaction_mail_send
# Create your views here.

class UserRegistrationView(FormView):
    template_name= 'accounts/user_register.html'
    form_class= UserRegistrationForm
    success_url= reverse_lazy('home')

    def form_valid(self, form):
        user= form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserLoginView(LoginView):
    template_name= 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('home')
    
class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('home')
    
class UserUpdateView(View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})

class UserPasswordChangeView(PasswordChangeView):
    template_name= 'accounts/change_password.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form) :
        transaction_mail_send(self.request.user, 0, 'Password Change', 'accounts/password_mail.html')
        return super().form_valid(form)
