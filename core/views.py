from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from .serializers import RegisterTeacherSerializer, ProfileSerializer, SchoolClassSerializer, StudentSerializer

from .permissions import IsAdmin
from .models import SchoolClass, Student
from .utils import generate_student_qr

User = get_user_model()

class RegisterTeacherView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterTeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Teacher created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user=User.objects.all()
        # serializer = ProfileSerializer(request.user)
        serializer = ProfileSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class SchoolClassCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = SchoolClassSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message':"Class created successfully","data":serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SchoolClassListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request):
        classes = SchoolClass.objects.all().order_by('-id')
        serializer = SchoolClassSerializer(classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SchoolClassDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get(self, request, pk):
        try:
            cls = SchoolClass.objects.get(pk=pk)
        except SchoolClass.DoesNotExist:
            return Response({"error":"class not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer = SchoolClassSerializer(cls)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SchoolClassUpdateView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    
    def put(self, request, pk):
        try:
            cls = SchoolClass.objects.get(pk=pk)
        except SchoolClass.DoesNotExist:
            return Response({"error":"class not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer = SchoolClassSerializer(cls, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message':"Class created successfully","data":serializer.data})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SchoolClassDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def delete(self, request, pk):
        try:
            cls = SchoolClass.objects.get(pk=pk)
        except SchoolClass.DoesNotExist:
            return Response({"error":"class not found"},status=status.HTTP_404_NOT_FOUND)
        
        cls.delete()
        return Response({'message':"Class Detele successfully"}, status=status.HTTP_200_OK)
    
class StudentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def post(self, request):
        serializer = StudentSerializer(data=request.data, context={"request":request})
        
        if serializer.is_valid():
            student = serializer.save()
            
            generate_student_qr(student)
            student.save()
            
            return Response(
                {"message":"Student created successfully","data":StudentSerializer(student, context={"request":request}).data},status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

class StudentListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        students = Student.objects.all().order_by('-id')
        serializer = StudentSerializer(students, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, data=request.data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student updated successfully", "data": serializer.data})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response({"message": "Student deleted successfully"}, status=status.HTTP_200_OK)
