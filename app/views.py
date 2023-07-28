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
            
        user = CustomUser(username=username, email=email, password=password)
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
        email = EmailMessage(mail_subject, message, to=[email])
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
            
        else:
            messages.error(request, 'Incorrect email address or password')
            
    return render(request, 'login.html')
            
@login_required(login_url='/login/')           
def userMessages(request):
    p = Paginator(UserMessage.objects.filter(user=request.user), 10)
    page = request.GET.get("page")
    myMessages = p.get_page(page)
    
    return render(request, 'messages.html', {"myMessages" : myMessages})
    
@login_required(login_url='/login/')
def userMessage(request, id):
    try:
        myMessage = UserMessage.objects.filter(user=request.user).get(id=id)
        myMessage.status = True
        myMessage.save()
        
    except:
        return render(request, '404.html')
    
    return render(request, 'message.html', {"myMessage" : myMessage})
 
    
@login_required(login_url='/login/')  
def deleteMessage(request, id):
    message = UserMessage.objects.get(id=id) 
    message.delete()
    return redirect("messages")


@login_required(login_url='/login/')   
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
            
            
@login_required(login_url='/login/')   
def changeUsername(request):
    if request.method == "POST":
        new_userrname = request.POST.get("new_username")
        password = request.POST.get("password")
        user = CustomUser.objects.get(email=request.user)
        if user.check_password(password):
            if CustomUser.objects.filter(username=new_userrname).exists():
                messages.error(request, 'Username already in use')
                
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
        UserMessage.objects.create(message=msg, user=user.email)
        messages.success(request, 'Message successfully sent')
        
    return render(request, 'sendmessage.html')
        
        
        
@login_required(login_url='/login/')       
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
                
                
            else:
                messages.error(request, 'Incorrect password')
            
        
        else:
            messages.error(request, 'Password does not match')
            
    return render(request, 'changepassword.html')
            
@login_required(login_url='/login/')           
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
    
@login_required(login_url='/login/')  
def logout(request):
    auth.logout(request)
    return redirect("login")

@login_required(login_url='/login/')
def settings(request):
    return render(request, 'settings.html')

@login_required(login_url='/login/')
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
    