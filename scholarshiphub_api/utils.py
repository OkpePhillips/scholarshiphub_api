from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import jwt


def send_verification_email(user):
    token = default_token_generator.make_token(user)
    verification_link = settings.API_BASE_URL + reverse('verify-email', kwargs={'uid': user.id, 'token': token})
    send_mail(
        'Verify your email',
        f'Please click the link to verify your email: {verification_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )