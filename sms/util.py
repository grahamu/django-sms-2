from sys import exc_info
from django.core.mail import send_mail
from django.db import transaction
from sms.models import OutboundMessage, ContentTypePhoneNumber

@transaction.commit_manually
def send_sms(msg, from_address, recipient_list, 
    fail_silently=False, auth_user=None, auth_password=None):
    """
    Send an SMS message to one or more recipients.
    
    The function signature is nearly identical to ``django.core.mail.send_mail``,
    with no ``subject`` and``recipient_list`` being a list of 
    ``ContentTypePhoneNumber`` objects instead of email addresses

    Messages that are not sent are not logged with ``OutboundMessage``
    
    TODO:   A bulk insert for the log data would probably be better, but
            iteration over the ``recipient_list`` should do for now.
    """
    
    if not from_address:
        raise Exception(u"Please specify a `from` email address!")
    
    # format the phone numbers into email gateways
    recipients = [
        recipient.generate_gateway_address()
        for recipient
        in recipient_list
    ]
    
    try:
        # send the sms message(s)
        send_mail("", msg, from_address, recipients, 
            False, auth_user, auth_password)
    except:
        if fail_silently:
            pass
        else:
            raise Exception(exc_info())
        transaction.rollback()
    else:
        # log delivery
        for recipient in recipient_list:
            logged_msg = OutboundMessage.objects.create(
                carrier = recipient.carrier,
                phone_number = recipient,
                from_address = from_address,
                message = msg
            )
        
        transaction.commit()

def format_date_range(start_date=None, end_date=None, fmt_string="%Y-%m-%d %H:%I:%S"):
    # TODO: this could be cleaned up
    if start_date and not end_date:
        sql_date_range = "where `created_date` >= '%s'" % start_date.strftime(date_fmt)
    elif end_date and not start_date:
        sql_date_range = "where `created_date` <= '%s'" % end_date.strftime(date_fmt)
    elif start_date and end_date:
        sql_date_range = """
            where `created_date` between '%s' and '%s'
        """ % (start_date.strftime(date_fmt), end_date.strftime(date_fmt))
    else:
        sql_date_range = ""
        
    return sql_date_range