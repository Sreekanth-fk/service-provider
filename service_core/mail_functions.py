from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings

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
        
    