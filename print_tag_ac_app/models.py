from django.db import models

# Create your models here.

class RefTag(models.Model):
    ref_id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return str(self.ref_id)  # Convert to string for a more descriptive representation
    
class Tag(models.Model):
    part_no = models.CharField(max_length= 255, blank=True, null=True)
    part_code = models.CharField(max_length= 255, blank=True, null=True)
    part_name = models.CharField(max_length= 255, blank=True, null=True)
    model_name = models.CharField(max_length= 255, blank=True, null=True)
    stock_inout = models.CharField(max_length= 255, blank=True, null=True)
    date = models.DateField(null=True, blank=True)
    whouse_code = models.CharField(max_length= 255, blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    ref_tag = models.ForeignKey(RefTag, on_delete=models.CASCADE)  # Foreign key field]