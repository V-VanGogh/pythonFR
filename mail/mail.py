import smtplib


def send_mail(patient, timestamp):
    gmail_user = 'information.project100@gmail.com'
    gmail_password = 'FJXAKOkTe9p4Por5GzEO$'

    sent_from = gmail_user
    to = 'nmath7@hotmail.com'
    subject = 'Area violation'
    body = 'Ο ασθενής ' + patient + 'βρέθηκε στην αίθουσα 1 στις ' + timestamp

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body.encode('utf-8'))



    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()
        print('Email sent!')
    except Exception as e:
        print(e)
