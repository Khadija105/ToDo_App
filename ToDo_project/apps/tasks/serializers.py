from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'due_date', 'created_at', 'updated_at', 'is_overdue']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue']
    
    def get_is_overdue(self, obj):
        return obj.is_overdue()
