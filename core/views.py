from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model
from .serializers import RegisterTeacherSerializer, ProfileSerializer, SchoolClassSerializer, StudentSerializer, AttendanceRecordSerializer

from .permissions import IsAdmin
from .models import SchoolClass, Student, AttendanceRecord
from .utils import generate_student_qr
from django.utils import timezone

from django.db.models import Count, Q
from datetime import datetime
from .report_utils import get_week_range, get_month_range

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
    
class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by("-id")
        serializer = ProfileSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteTeacherView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, teacher_id):
        # Step 1: Find teacher
        try:
            teacher = User.objects.get(id=teacher_id, role="TEACHER")
        except User.DoesNotExist:
            return Response({"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Prevent admin self delete
        if teacher.id == request.user.id:
            return Response({"error": "Admin cannot delete own account"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Remove teacher from assigned classes
        SchoolClass.objects.filter(class_teacher=teacher).update(class_teacher=None)

        # Step 4: Soft delete
        teacher.is_active = False
        teacher.is_deleted = True
        teacher.save()

        return Response({"message": "Teacher deleted (soft delete) successfully"}, status=status.HTTP_200_OK)

    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TeacherListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        teachers = User.objects.filter(
            role="TEACHER",
            is_deleted=False,
            is_active=True
        ).order_by("-id")

        serializer = ProfileSerializer(teachers, many=True)
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        classes = SchoolClass.objects.all().order_by('-id')
        serializer = SchoolClassSerializer(classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SchoolClassDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = Student.objects.all().order_by('-id')
        serializer = StudentSerializer(students, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class StudentDetailView(APIView):
    permission_classes = [IsAuthenticated]

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

class MarkAttendanceByQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Step 1: Role check (only teachers/admin allowed)
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response({"error": "You are not allowed to mark attendance"}, status=status.HTTP_403_FORBIDDEN)

        # Step 2: Get QR data from request
        qr_data = request.data.get("qr_data")
        if not qr_data:
            return Response({"error": "qr_data is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Split QR data
        try:
            student_uid, class_id, verification_key = qr_data.split("|")
        except ValueError:
            return Response({"error": "Invalid QR format"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Find student by UUID
        try:
            student = Student.objects.get(student_uid=student_uid)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Step 5: Validate class
        if str(student.student_class.id) != str(class_id):
            return Response({"error": "Class mismatch"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 6: Validate verification key
        if student.verification_key != verification_key:
            return Response({"error": "Verification failed"}, status=status.HTTP_401_UNAUTHORIZED)

        # Step 7: Prevent duplicate attendance for same day
        today = timezone.now().date()
        if AttendanceRecord.objects.filter(student=student, date=today).exists():
            return Response({"error": "Attendance already marked today"}, status=status.HTTP_409_CONFLICT)

        # Step 8: Create attendance record
        attendance = AttendanceRecord.objects.create(
            student=student,
            student_class=student.student_class,
            date=today,
            status='P',
            marked_by=request.user,
            method="QR"
        )

        # Step 9: Return response
        serializer = AttendanceRecordSerializer(attendance)
        return Response(
            {"message": "Attendance marked successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

class TodayAttendanceByClassView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        today = timezone.now().date()

        records = AttendanceRecord.objects.filter(
            student_class_id=class_id,
            date=today
        ).order_by('-marked_at')

        serializer = AttendanceRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DailyAttendanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        # Step 1: teacher/admin check
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        # Step 2: read date param (?date=YYYY-MM-DD)
        date_str = request.query_params.get("date")
        if date_str:
            try:
                report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            report_date = timezone.now().date()

        # Step 3: fetch attendance records
        records = AttendanceRecord.objects.filter(
            student_class_id=class_id,
            date=report_date
        )

        # Step 4: summary counts
        total_present = records.filter(status="P").count()
        total_absent = records.filter(status="A").count()

        return Response({
            "class_id": class_id,
            "date": str(report_date),
            "total_present": total_present,
            "total_absent": total_absent,
            "total_marked": records.count(),
            "records": AttendanceRecordSerializer(records, many=True).data
        }, status=status.HTTP_200_OK)

class WeeklyAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        # read optional date param
        date_str = request.query_params.get("date")
        if date_str:
            try:
                base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            base_date = timezone.now().date()

        week_start, week_end = get_week_range(base_date)

        # fetch records for week
        records = AttendanceRecord.objects.filter(
            student_class_id=class_id,
            date__range=[week_start, week_end]
        )

        # count status
        present_count = records.filter(status="P").count()
        absent_count = records.filter(status="A").count()

        return Response({
            "class_id": class_id,
            "week_start": str(week_start),
            "week_end": str(week_end),
            "present_count": present_count,
            "absent_count": absent_count,
            "total_marked": records.count(),
        }, status=status.HTTP_200_OK)

class MonthlyAttendanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, class_id):
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        date_str = request.query_params.get("date")
        if date_str:
            try:
                base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            base_date = timezone.now().date()

        month_start, month_end = get_month_range(base_date)

        records = AttendanceRecord.objects.filter(
            student_class_id=class_id,
            date__range=[month_start, month_end]
        )

        present_count = records.filter(status="P").count()
        absent_count = records.filter(status="A").count()
        total_marked = records.count()

        # percentage calculation
        attendance_percent = 0
        if total_marked > 0:
            attendance_percent = round((present_count / total_marked) * 100, 2)

        return Response({
            "class_id": class_id,
            "month_start": str(month_start),
            "month_end": str(month_end),
            "present_count": present_count,
            "absent_count": absent_count,
            "total_marked": total_marked,
            "attendance_percent": attendance_percent
        }, status=status.HTTP_200_OK)

class StudentAttendanceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        if request.user.role not in ['TEACHER', 'ADMIN']:
            return Response({"error": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        # optional filters
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")

        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        records = AttendanceRecord.objects.filter(student=student).order_by("-date")

        # apply date filtering if provided
        if from_date and to_date:
            try:
                from_d = datetime.strptime(from_date, "%Y-%m-%d").date()
                to_d = datetime.strptime(to_date, "%Y-%m-%d").date()
                records = records.filter(date__range=[from_d, to_d])
            except ValueError:
                return Response({"error": "Invalid from/to date format. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        present_count = records.filter(status="P").count()
        absent_count = records.filter(status="A").count()
        total = records.count()

        percent = 0
        if total > 0:
            percent = round((present_count / total) * 100, 2)

        return Response({
            "student_id": student_id,
            "student_name": student.full_name,
            "class": str(student.student_class),
            "present_count": present_count,
            "absent_count": absent_count,
            "total_days": total,
            "attendance_percent": percent,
            "records": AttendanceRecordSerializer(records, many=True).data
        }, status=status.HTTP_200_OK)

class AdminDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()

        # Totals
        total_students = Student.objects.count()
        total_classes = SchoolClass.objects.count()
        total_teachers = User.objects.filter(role="TEACHER").count()

        # Today's attendance
        today_records = AttendanceRecord.objects.filter(date=today)
        present_today = today_records.filter(status="P").count()
        absent_today = today_records.filter(status="A").count()

        total_marked_today = today_records.count()

        attendance_percent = 0
        if total_marked_today > 0:
            attendance_percent = round((present_today / total_marked_today) * 100, 2)

        return Response({
            "date": str(today),
            "totals": {
                "students": total_students,
                "classes": total_classes,
                "teachers": total_teachers,
            },
            "today_attendance": {
                "marked": total_marked_today,
                "present": present_today,
                "absent": absent_today,
                "attendance_percent": attendance_percent
            }
        }, status=status.HTTP_200_OK)

class AdminTodayClassWiseAttendanceView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()

        classes = SchoolClass.objects.all().order_by("class_name", "section")

        result = []

        for cls in classes:
            records = AttendanceRecord.objects.filter(student_class=cls, date=today)
            present_count = records.filter(status="P").count()
            absent_count = records.filter(status="A").count()
            total = records.count()

            percent = 0
            if total > 0:
                percent = round((present_count / total) * 100, 2)

            result.append({
                "class_id": cls.id,
                "class_name": str(cls),
                "present": present_count,
                "absent": absent_count,
                "total_marked": total,
                "attendance_percent": percent
            })

        return Response({
            "date": str(today),
            "classes": result
        }, status=status.HTTP_200_OK)

class TeacherDashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # only teacher allowed
        if request.user.role != "TEACHER":
            return Response({"error": "Only teacher can access this dashboard"}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()

        assigned_classes = SchoolClass.objects.filter(class_teacher=request.user)

        class_ids = assigned_classes.values_list("id", flat=True)

        total_students = Student.objects.filter(student_class_id__in=class_ids).count()

        today_records = AttendanceRecord.objects.filter(
            student_class_id__in=class_ids,
            date=today
        )
        present_today = today_records.filter(status="P").count()
        absent_today = today_records.filter(status="A").count()

        return Response({
            "teacher": request.user.username,
            "date": str(today),
            "assigned_classes": [
                {"id": cls.id, "name": str(cls)} for cls in assigned_classes
            ],
            "summary": {
                "total_students": total_students,
                "marked_today": today_records.count(),
                "present_today": present_today,
                "absent_today": absent_today,
            }
        }, status=status.HTTP_200_OK)

class TeacherTodayAbsentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "TEACHER":
            return Response({"error": "Only teacher can access this"}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.now().date()
        assigned_classes = SchoolClass.objects.filter(class_teacher=request.user)
        class_ids = assigned_classes.values_list("id", flat=True)

        absent_records = AttendanceRecord.objects.filter(
            student_class_id__in=class_ids,
            date=today,
            status="A"
        ).order_by("student__full_name")

        data = AttendanceRecordSerializer(absent_records, many=True).data

        return Response({
            "date": str(today),
            "absent_records": data
        }, status=status.HTTP_200_OK)
