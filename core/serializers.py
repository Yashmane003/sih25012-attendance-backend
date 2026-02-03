from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SchoolClass, Student, AttendanceRecord
from rest_framework.exceptions import ValidationError
User = get_user_model()

class RegisterTeacherSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=['ADMIN', 'TEACHER'],
        required=True  # Make role required
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role']
    
    def validate_role(self, value):
        """Ensure only one ADMIN exists"""
        if value == 'ADMIN':
            # Check if an admin already exists
            if User.objects.filter(role='ADMIN').exists():
                raise ValidationError("An admin already exists in the system. Only one admin is allowed.")
        return value
    
    def create(self, validated_data):
        role = validated_data.pop('role')  # Extract role
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        user.role = role
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
    


class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField(read_only=True)
    qr_code_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id',
            'student_uid',
            'full_name',
            'roll_no',
            'student_class',
            'class_name',
            'guardian_mobile',
            'verification_key',
            'qr_code_image',
            'qr_code_url',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['student_uid', 'verification_key', 'qr_code_image']

    def get_class_name(self, obj):
        return str(obj.student_class)

    def get_qr_code_url(self, obj):
        request = self.context.get("request")
        if obj.qr_code_image and request:
            return request.build_absolute_uri(obj.qr_code_image.url)
        return None



class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    class_name = serializers.SerializerMethodField(read_only=True)
    marked_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id',
            'student',
            'student_name',
            'student_class',
            'class_name',
            'date',
            'status',
            'marked_by',
            'marked_by_name',
            'marked_at',
            'method'
        ]
        read_only_fields = ['marked_by', 'marked_at', 'method']

    def get_student_name(self, obj):
        return obj.student.full_name

    def get_class_name(self, obj):
        return str(obj.student_class)

    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return obj.marked_by.username
        return None
