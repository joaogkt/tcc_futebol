from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import VerificationCode
from django.contrib.auth.models import User
import random
import string
import smtplib
from smtplib import SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('home')
        else:
            form_login = AuthenticationForm()
            error_message = "Credenciais inválidas. Tente novamente."
            return render(request, 'login.html', {
                'form_login': form_login,
                'error_message': error_message,
            })
    else:
        form_login = AuthenticationForm()
    return render(request, 'login.html', {'form_login': form_login})


def generate_code():
    """Gera um código de 6 dígitos para a verificação."""
    return ''.join(random.choices(string.digits, k=6))


def register(request):
    if request.method == "POST":
        form_usuario = CustomUserCreationForm(request.POST)
        if form_usuario.is_valid():
            email = request.POST.get('email')
            print(f"EMAIL RECEBIDO NO FORMULÁRIO: {email}")
            user = form_usuario.save(commit=False)
            user.is_active = False
            user.save()

            code = generate_code()
            print(f"CÓDIGO GERADO: {code}") 

            VerificationCode.objects.create(user=user, code=code)

            print(f"Chamando send_email({code}, {email})") 

            try:
                send_email(code, email)
                messages.success(request, "Conta criada! Verifique seu e-mail e insira o código para ativá-la. Verifique a caixa de spam.")
                print("Redirecionando para a página de verificação...")

                return redirect('verify')
            except Exception as e:
                print(f"Erro ao enviar e-mail: {e}") 
                messages.error(request, f"Erro ao enviar o e-mail: {e}")
                print("Redirecionando para a página de verificação...")

                return render(request, 'register.html', {'form_usuario': form_usuario})

    else:
        form_usuario = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form_usuario': form_usuario})



def verify(request):
    """Tela de verificação do código enviado por e-mail"""
    if request.method == "POST":
        code = request.POST.get('verification_code', '').strip()

        if not code:
            messages.error(request, "Por favor, insira o código de verificação. Se não estiver no email verifique a caixa de spam.")
            return render(request, 'verify.html')

        try:
            verification = VerificationCode.objects.get(code=code)
            user = verification.user 

            user.is_active = True
            user.save()
            verification.delete()

            messages.success(request, "Conta ativada! Agora você pode fazer login.")
            return redirect('login')

        except VerificationCode.DoesNotExist:
            messages.error(request, "Código inválido ou expirado.")

    return render(request, 'verify.html')

    

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


def send_email(code, email):
    sender_email = "game.vision.udf@gmail.com"
    receiver_email = email
    password = "ljnv rosa drnr nwwl"
    
    subject = "Código de Verificação - Game Vision"
    body = f'Seu código de verificação é: {code}'
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    try:
        print("Conectando ao servidor SMTP...") 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        
        print("Enviando e-mail...") 
        server.sendmail(sender_email, receiver_email, msg.as_string())

        print("E-mail enviado com sucesso!") 
        
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
    finally:
        server.quit()
        print("Conexão encerrada com SMTP.")