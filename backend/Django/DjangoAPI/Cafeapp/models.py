from django.db import models

# Create your models here.

class Store_labels(models.Model):
    link = models.CharField(max_length=10000)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    time = models.CharField(max_length=1000)
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=1000)
    img = models.CharField(max_length=1000)
    website = models.CharField(max_length=500)
    star = models.FloatField()
    review_num = models.IntegerField()
    labels = models.CharField(max_length=5000)


class Review_tokens(models.Model):
    link = models.CharField(max_length=10000)
    review = models.CharField(max_length=10000)
    review_time = models.CharField(max_length=10000)
    Cafeid = models.CharField(max_length=10000, default="default")
    name = models.CharField(max_length=10000)
    review_tokenization = models.CharField(max_length=10000)    