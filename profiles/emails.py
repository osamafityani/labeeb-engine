from django.core.mail import send_mail, get_connection
from django.conf import settings


def send_new_password(email, new_password):
    subject = 'Tax Prime Password Reset'
    message = (f"You requested a password reset for your account. Don't share the contents of this email at any"
               f" circumstances.\nYour new password is: {new_password}\nThis is an automated service, don't reply to "
               f"this email.")
    email_from = settings.EMAIL_HOST
    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username='passwordreset@j-1.org',
                                password='shfkgauyevustnva',
                                use_tls=True)

    send_mail(subject, message, email_from, [email], connection=connection)
    connection.close()


def send_estimates_ready_update(email):
    subject = 'Your federal and state tax refund values are here! Check them out.'
    message = """Congratulations! 
Your documents have been processed and your tax estimate is ready. You may now log back into the app to see your tax statement and finish filing your return. 

Thank you for trusting us! 

The professionals at
TaxPrime

P.S. Don't forget to refer your friends and earn $!!"""
    email_from = settings.EMAIL_HOST
    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username='noreply@j-1.org',
                                password='lmpxmqpffmseoxzw',
                                use_tls=True)

    send_mail(subject, message, email_from, [email], connection=connection)
    connection.close()


def send_ty_and_status(email):
    subject = 'TaxPrime: Your tax return is under processing.'
    message = (f"Thank you for choosing TaxPrime for your J1 tax refund. We recieved your information"
               f" and you will be getting your refund soon. You can check the status of your federal"
               f" refund here: https://sa.www4.irs.gov/wmr/shared_secrets \n\n"
               f"In the meantime, if you have any questions feel free to reach for us at"
               f"help@j-1.org \n"
               f"TaxPrime team.")  # TODO: replace url when site is published
    email_from = settings.EMAIL_HOST
    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username='noreply@j-1.org',
                                password='lmpxmqpffmseoxzw',
                                use_tls=True)

    send_mail(subject, message, email_from, [email], connection=connection)
    connection.close()


def notify_preparer_new_profile(profile, email):
    if 'test' in profile.first_name + ' ' + profile.last_name + ' ' + profile.user.email:
        return
    subject = 'A new profile has been created'
    message = (f'A new profile has been created.\n'
               f'email: {profile.user.email}'
               f'first_name: {profile.first_name}'
               f'last_name: {profile.last_name}')
    email_from = settings.EMAIL_HOST
    connection = get_connection(host=settings.EMAIL_HOST,
                                port=settings.EMAIL_PORT,
                                username='noreply@j-1.org',
                                password='lmpxmqpffmseoxzw',
                                use_tls=True)

    send_mail(subject, message, email_from, [email], connection=connection)
    connection.close()


def notify_preparer_stage1_issues(profile, email):
    issues = []

    if profile.income_out_of_range:
        issues.append("Income out of range")
    if profile.medicare_withheld:
        issues.append("Medicare tax withheld")
    if profile.social_withheld:
        issues.append("Social security tax withheld")
    if profile.w2_edited:
        issues.append("W2 data was edited by user after OCR")
    if profile.multiple_states:
        issues.append("Multiple W2s for multiple states")
    if profile.tax_treaty_country:
        issues.append("Tax treaty country")

    if len(issues) > 0:
        subject = 'Resolve issues to clear for UT'
        message = (f"Name: {profile.first_name} {profile.last_name}\n"
                   f"Email: {profile.user.email}\n"
                   f"Status: App phase 1 complete.\n"
                   f"Known issues:{', '.join(issues)}")
        email_from = settings.EMAIL_HOST
        connection = get_connection(host=settings.EMAIL_HOST,
                                    port=settings.EMAIL_PORT,
                                    username='noreply@j-1.org',
                                    password='lmpxmqpffmseoxzw',
                                    use_tls=True)

        send_mail(subject, message, email_from, [email], connection=connection)
        connection.close()

