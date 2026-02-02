from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SchoolClass

User = get_user_model()

class RegisterTeacherSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id','username','email','password','role']
        
        extra_kwargs = {
            'role':{'read_only':True}
        }
        
        def create(self, validated_data):
            user = User(
                username=validated_data['username'],
                email=validated_data.get('email','')
            )
            user.set_password(validated_data['password'])
            user.role = 'TEACHER'
            user.save()
            return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','role']

class SchoolClassSerializer(serializers.ModelSerializer):
    class_teacher_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = SchoolClass
        fields = [
            'id',
            'class_name',
            'section',
            'class_teacher',
            'class_teacher_name',
            'created_at'
        ]
        
    def get_class_teacher_name(self, obj):
        if obj.class_teacher:
            return obj.class_teacher.username
        return None