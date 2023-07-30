from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages, auth
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import email_verification_token
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.conf import settings
from random import randint

# Create your views here.
def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email address in use')
            
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username in use')
            
        user = CustomUser(username=username, email=email)
        user.set_password(password)
        user.is_active = False
        user.save()
        
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        
        #Email Message
        mail_subject = 'Activate your Account'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'uid': uid,
            'token': token,
            'domain': current_site
        })
        email = EmailMessage(mail_subject, message, 'myanonimomessage@gmail.com' , [email])
        email.content_subtype = "html"
        if email:
            email.send()
            messages.success(request, 'Activation Link has been sent to your mail')
        
    return render(request, 'register.html')
        
        
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = auth.authenticate(username=email, password=password)
        next = request.GET.get("next")
        if user is not None:
            auth.login(request, user)
            
            
            if 'next' in request.GET:
                return redirect(next)
            
            
            return redirect("dashboard")
            
        else:
            messages.error(request, 'Incorrect email address or password')
            
    return render(request, 'login.html')


@login_required(login_url='/login')           
def dashboard(request):
    return render(request, 'dashboard.html')
            
@login_required(login_url='/login')           
def userMessages(request):
    p = Paginator(UserMessage.objects.filter(user=request.user).order_by('-date_added'), 10)
    page = request.GET.get("page")
    myMessages = p.get_page(page)
    
    return render(request, 'messages.html', {"myMessages" : myMessages})
    
    
@login_required(login_url='/login')  
def deleteMessage(request, id):
    try:
        message = UserMessage.objects.filter(user=request.user).get(id=id) 
    except UserMessage.DoesNotExist:
        return render(request, '404.html')
    message.delete()
    messages.success(request, 'Message deleted')
    return redirect("userMessages")


@login_required(login_url='/login')   
def changeEmail(request):
    if request.method == "POST":
        new_email = request.POST.get("new_email")
        password = request.POST.get("password")
        user = CustomUser.objects.get(email=request.user)
        if user.check_password(password):
            if CustomUser.objects.filter(email=new_email).exists():
                messages.error(request, 'Email address already in use')
                
            user.email = new_email
            user.save()
            messages.success(request, 'Email address successfully updated')
        
        else:
            messages.error(request, 'Incorrect password')
            
    return render(request, 'changeemail.html')
            
            
@login_required(login_url='/login')   
def changeUsername(request):
    if request.method == "POST":
        new_userrname = request.POST.get("new_username")
        password = request.POST.get("password")
        user = CustomUser.objects.get(email=request.user)
        if user.check_password(password):
            
            if CustomUser.objects.filter(username=new_userrname).exists():
                messages.error(request, 'Username already in use')
                
            else:
                 user.username = new_userrname
                 user.save()
                 messages.success(request, 'Username successfully updated')
        
        else:
            messages.error(request, 'Incorrect password')    
            
    return render(request, 'changeusername.html')       
                
        
        
def sendMessage(request):
    if request.method == "POST":
        msg = request.POST.get("msg")
        username = request.GET.get("user")
        user= CustomUser.objects.get(username=username)
        UserMessage.objects.create(message=msg, user=user)
        messages.success(request, 'Message successfully sent')
        
    return render(request, 'sendmessage.html')
        
        
        
@login_required(login_url='/login')       
def changePassword(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        cpassword = request.POST.get("cpassword")
        user = CustomUser.objects.get(email=request.user)
        
        if cpassword == new_password:
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated')
                
                
            else:
                messages.error(request, 'Incorrect password')
            
        
        else:
            messages.error(request, 'Password does not match')
            
    return render(request, 'changepassword.html')
            
@login_required(login_url='/login')           
def editProfile(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        
        user = CustomUser.objects.get(email=request.user)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        messages.success(request, 'Profile successfully updated')
        
    return render(request, 'editprofile.html')
    
@login_required(login_url='/login')  
def logout(request):
    auth.logout(request)
    return redirect("login")

@login_required(login_url='/login')
def settings(request):
    return render(request, 'settings.html')

@login_required(login_url='/login')
def notifications(request):
    p = Paginator(Notification.objects.filter(user=request.user), 15)
    page = request.GET.get("page")
    user_notifications = p.get_page(page)
    return render(request, 'notifications.html', {"notifications": user_notifications})



def activate_user_account(request, token, uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        if user is not None and email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            auth.login(request, user)
            return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        
        else:
            return HttpResponse('Activation link is invalid!')
        
    except:
        return HttpResponse('Bad Request')
    
@login_required(login_url='/login')   
def profile(request):
    return render(request, 'profile.html')
    
    

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user= CustomUser.objects.get(email=email)
            
        except CustomUser.DoesNotExist:
            return render(request, '404.html')
        if CustomUser.objects.filter(email=user).exists():
            if Token.objects.filter(user=user).exists:
                token = Token.objects.filter(user=user)
                token.delete()
                
                token = Token(user=user, code=randint(100000, 900000))
                token.save()
                email_message = EmailMessage('Password Reset', f'Your code is {token.code}.',  'myanonimomessage@gmail.com', [email] )
                email_message.send()
                messages.success(request, 'Enter code sent to your mail')
                return render(request, 'reset_token_confirmation.html')
                
            
            token = Token(user=user, code=randint(100000, 900000))
            token.save()
            email_message = EmailMessage('Password Reset', f'Your code is {token.code}.', [email] )
            email_message.send()
            messages.success(request, 'Enter code sent to your mail')
            return render(request, 'reset_token_confirmation.html', {"email": user})
            
        
        else:
            messages.error(request, 'Account does not exist')
            
    return render(request, 'reset_password.html')
            
            
            
def reset_token_confirmation(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")
        user= CustomUser.objects.get(email=email)
        user_code = Token.objects.get(user=user)
        if code == user_code:
            default_password = randint(10000, 90000)
            user= CustomUser.objects.get(email=user)
            user.set_password(default_password)
            user.save()
            email = EmailMessage('New Password Reset', f'Your new password is {default_password}, kindly ensure you change it after logging in.', 'myanonimomessage@gmail.com', [email] )
            email.send()
            return HttpResponse(request, 'A default password has been sent to your mail')
            
            
        else:
            return HttpResponse(request, 'An error occurred')