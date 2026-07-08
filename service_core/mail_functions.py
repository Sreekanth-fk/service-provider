from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from apps.user.models import CheckLogs

"""------------------------------ EMAIL SENDING ---------------------------------------------"""

class SendEmails:
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def sendTemplateEmail(self, subject,  context, template, email_host, user_email, reply_to=[]):
        sending_status = False
        # import pdb; pdb.set_trace()
        
        try:
            context = context
            # image = request.build_absolute_uri("/")
            # context['image']    = str(image)+''
            html_content = render_to_string(str(template), {'context':context})
            text_content = strip_tags(html_content)
            send_e = EmailMultiAlternatives(str(subject), text_content, email_host, [user_email],reply_to=reply_to )
            send_e.attach_alternative(html_content, "text/html")
            send_e.send()

            sending_status = True
        except Exception as es:
           return es      
        
    def sendTemplateEmailList(self, subject,  context, template, email_host, user_email,reply_to=[]):
        sending_status = False
        
        try:
            context = context
            # image = request.build_absolute_uri("/")
            # context['image']    = str(image)+''
            html_content = render_to_string(str(template), {'context':context})
            text_content = strip_tags(html_content)
            send_e = EmailMultiAlternatives(str(subject), text_content, email_host, user_email,reply_to=reply_to )
            send_e.attach_alternative(html_content, "text/html")
            send_e.send()

            sending_status = True
            
        except Exception as es:
           return es    

    def sendTemplateEmailCC(self, subject, request, context, template, email_host, user_email):
        sending_status = False
        try:
            context = context
            image = request.build_absolute_uri("/")
            context['image']    = str(image)+''
            html_content = render_to_string(str(template), {'context':context})
            text_content = strip_tags(html_content)
            send_e = EmailMultiAlternatives(str(subject), text_content, email_host, [str(user_email),str(settings.CC_EMAIL)] )
            send_e.attach_alternative(html_content, "text/html")
            send_e.send()

            sending_status = True
        except Exception as es:
           pass
        return sending_status
    
    def sendTemplateEmailwithPdf(self, subject, request,  template, email_host, user_email, pdf_file=None, 
                             pdf_file2=None, pdf_file_name=None,pdf_file2_name=None):

        sending_status = False
        try:
           
            send_e = EmailMultiAlternatives(subject, template, email_host, [str(user_email),str(settings.CC_EMAIL)])
            send_e.attach_alternative(template, "text/html")
            
            if pdf_file:
                pdf_file_name = pdf_file_name if pdf_file_name else 'document1.pdf'
                send_e.attach(pdf_file_name, pdf_file.read(), 'application/pdf')

            if pdf_file2:
                pdf_file2_name = pdf_file2_name if pdf_file2_name else 'document2.pdf'
                send_e.attach(pdf_file2_name, pdf_file2.read(), 'application/pdf')


            
            send_e.send()

            sending_status = True
        except Exception as es:
            print("Error sending email:", es)
        return sending_status
        