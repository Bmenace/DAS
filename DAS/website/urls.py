from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register_students/', views.register_students, name='register_students'),
    path('save-data/', views.save_data, name='save_data'),
    path('get-registered-students/', views.get_registered_students, name='get_registered_students'),
    path('registered-students/', views.registered_students_view, name='registered_students'),
    path('delete-student/<path:student_id>/', views.delete_student, name='delete_student'),
    path('year-semester/', views.save_selection, name='year_semester_page'),
    path('delete-record/<int:record_id>/', views.delete_record, name='delete_record'),
    path('units/<int:year>/<int:semester>/', views.units_page, name='units_page'),
    path('delete_unit/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    path('get-data/', views.get_data, name='get_data'),
    path('save-attendance/', views.save_attendance, name='save_attendance'),
    path('fetch-saved-attendance/', views.fetch_saved_attendance, name='fetch_saved_attendance'),
    path('select_lectures/', views.select_lectures, name='select_lectures'), 
    path('year-semester-list/', views.year_semester_list, name='year_semester_list'),
    path('attendance/<int:year_id>/<int:semester_id>/', views.attendance_page, name='attendance_page'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("student-progress/<int:student_id>/", views.student_progress, name="student_progress"),


 ]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])