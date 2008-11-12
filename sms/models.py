from datetime import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import connection, models, transaction
from sms.managers import PhoneNumberManager

class Carrier(models.Model):
    """
    A ``Carrier`` describes the email-to-SMS gateway
    offered by a phone service provider such as AT&T, 
    T-Mobile, and so on.
    
    The ``gateway`` should always be: 
        ``%(phone_number)s@[gateway email address]``
    """
    name = models.CharField(max_length=120)
    gateway = models.CharField(max_length=120)
    
    class Meta:
        ordering = ('name',)
        unique_together = (("name", "gateway"),)
        verbose_name = u"Carrier"
        verbose_name_plural = u"Carriers"
    
    def __unicode__(self):
        return self.name
        
        
class ContentTypePhoneNumber(models.Model):
    content_type = models.ForeignKey(ContentType, related_name="phone_numbers")
    object_id = models.PositiveIntegerField()
    carrier = models.ForeignKey(Carrier, related_name="phone_numbers")
    phone_number = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_primary_number = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=datetime.now)
    
    content_object = generic.GenericForeignKey()
    objects = PhoneNumberManager()
    
    class Meta:
        ordering = ('content_type', '-carrier', '-is_primary_number')
        unique_together = (
            ("content_type", "object_id", "phone_number"),
            ("content_type", "object_id", "phone_number", "is_primary_number"),
        )
        verbose_name = u"Phone Number"
        verbose_name_plural = u"Phone Numbers"
        
    def __unicode__(self):
        return "%s (%s)" % (self.phone_number, self.carrier.name)
        
    def save(self, force_insert=False, force_update=False):
        """
        Validate that the phone number being inserted has nothing other
        than [0-9]
        """
        from re import sub
        
        # replace !0-9 chars
        self.phone_number = sub(r"[^\d]", "", self.phone_number)
        
        super(ContentTypePhoneNumber, self).save(force_insert, force_update)
        
    def generate_gateway_address(self):
        return self.carrier.gateway % {'phone_number': self.phone_number}
        

class OutboundMessageManager(models.Manager):
    """
    Help with pulling neat things from the data
    """
            
    def most_popular_carriers(self, start_date=None, end_date=None, offset=0, limit=25):
        """
        Get a list of the most popular ``Carrier``, optionally
        within a specific date range.

        ``start_date`` and ``end_date`` should be ``datetime`` objects.
        """
        from sms.util import format_date_range

        cursor = connection.cursor()

        query = """
            select 
                count(*) `carrier_weight`,
                `carrier_id`
            from 
                `sms_outboundmessage`
        """
            
        query += format_date_range(start_date, end_date)
        
        query += """
            group by 
                `carrier_id`
            order by
                `carrier_weight` desc
            limit %(offset)s,%(limit)s;
        """
        
        query = query % {
            'offset': offset,
            'limit': limit
        }
        
        cursor.execute(query)
        results = cursor.fetchall()

        pks = [result[1] for result in results]
        bulk_dict = Carrier.objects.in_bulk(pks)

        return [bulk_dict[pk] for pk in pks]
        
    def most_contacted_numbers(self, start_date=None, end_date=None, offset=0, limit=25):
        """
        Get a list of the most active ``ContentTypePhoneNumber``s
        """
        from sms.util import format_date_range
        
        cursor = connection.cursor()

        query = """
            select 
                count(*) `recipient_weight`,
                `phone_number_id`
            from 
                `sms_outboundmessage`
        """
            
        query += format_date_range(start_date, end_date)
        
        query += """
            group by 
                `phone_number_id`
            order by
                `recipient_weight` desc
            limit %(offset)s,%(limit)s;
        """
        
        query = query % {
            'offset': offset,
            'limit': limit
        }
        
        cursor.execute(query)
        results = cursor.fetchall()

        pks = [result[1] for result in results]
        bulk_dict = ContentTypePhoneNumber.objects.select_related('content_type').in_bulk(pks)

        return [bulk_dict[pk] for pk in pks]      


class OutboundMessage(models.Model):
    """
    An ``OutboundMessage`` is a log that kept for tracking
    ``Carrier`` and ``ContentTypePhoneNumber`` usage.
    """
    carrier = models.ForeignKey(Carrier, related_name="summary")
    phone_number = models.ForeignKey(ContentTypePhoneNumber, related_name="summary")
    from_address = models.CharField(max_length=120)
    message = models.CharField(max_length=255, blank=True, null=True)
    created_date = models.DateTimeField(default=datetime.now)
    
    objects = OutboundMessageManager()
    
    class Meta:
        ordering = ('-created_date', '-id')
        verbose_name = u"Outbound Message Log Entry"
        verbose_name_plural = u"Outbound Message Log Entries"
    
    def __unicode__(self):
        return self.phone_number.__unicode__()