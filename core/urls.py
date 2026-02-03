from django.urls import path
from .views import (RegisterTeacherView, 
    ProfileView,
    SchoolClassCreateView,
    SchoolClassListView,
    SchoolClassDetailView,
    SchoolClassUpdateView,
    SchoolClassDeleteView,
    StudentCreateView,
    StudentListView,
    StudentDetailView,
    StudentUpdateView,
    StudentDeleteView,
    MarkAttendanceByQRView,
    TodayAttendanceByClassView,
    DailyAttendanceReportView,
    WeeklyAttendanceSummaryView,
    MonthlyAttendanceSummaryView,
    StudentAttendanceHistoryView,
    AdminDashboardOverviewView,
    AdminTodayClassWiseAttendanceView,
    TeacherDashboardOverviewView,
    TeacherTodayAbsentListView,
)
urlpatterns = [
    path('register-teacher/', RegisterTeacherView.as_view(), name='register_teacher'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # Phase 2 - Class Module
    path('classes/create/', SchoolClassCreateView.as_view(), name='class_create'),
    path('classes/', SchoolClassListView.as_view(), name='class_list'),
    path('classes/<int:pk>/', SchoolClassDetailView.as_view(), name='class_detail'),
    path('classes/<int:pk>/update/', SchoolClassUpdateView.as_view(), name='class_update'),
    path('classes/<int:pk>/delete/', SchoolClassDeleteView.as_view(), name='class_delete'),
    
    # Phase 3 - Student Module
    path('students/create/', StudentCreateView.as_view(), name='student_create'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    
    # Phase 4 - Attendance
    path('attendance/mark/', MarkAttendanceByQRView.as_view(), name='mark_attendance_qr'),
    path('attendance/today/<int:class_id>/', TodayAttendanceByClassView.as_view(), name='today_attendance'),
    
    # Phase 5 - Reports
    path("reports/daily/<int:class_id>/", DailyAttendanceReportView.as_view(), name="daily_report"),
    path("reports/weekly/<int:class_id>/", WeeklyAttendanceSummaryView.as_view(), name="weekly_report"),
    path("reports/monthly/<int:class_id>/", MonthlyAttendanceSummaryView.as_view(), name="monthly_report"),
    path("reports/student/<int:student_id>/", StudentAttendanceHistoryView.as_view(), name="student_history"),
    
     # Phase 6 - Dashboard APIs
    path("dashboard/admin/overview/", AdminDashboardOverviewView.as_view(), name="admin_dashboard_overview"),
    path("dashboard/admin/classwise-today/", AdminTodayClassWiseAttendanceView.as_view(), name="admin_classwise_today"),
    path("dashboard/teacher/overview/", TeacherDashboardOverviewView.as_view(), name="teacher_dashboard_overview"),
    path("dashboard/teacher/absent-today/", TeacherTodayAbsentListView.as_view(), name="teacher_absent_today"),
]

