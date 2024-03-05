from rest_framework import serializers
from .models import Store_labels

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store_labels
        fields = '__all__'