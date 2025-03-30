from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from .models import Student, ScannedData, Profile, YearRecord, Attendance, Lecture, Unit
from django.shortcuts import render, redirect
import urllib.parse
from django.views.decorators.cache import cache_control
from django.db import IntegrityError
from django.db.models import Count, Avg
from django.db import transaction




# Create your views here.
def home(request):
    return render(request, 'home.html', {})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect if already logged in

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')  # Get selected role from dropdown

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:  # Check if the user is verified by admin
                login(request, user)
                messages.success(request, 'You have successfully logged in.')

                # Redirect based on role
                if role == "class_rep":
                    return redirect('home')
                elif role == "lecturer":
                    return redirect('lecturer_dashboard')
                else:
                    return redirect('home')

            else:
                messages.error(request, 'Your account is pending admin approval.')
        else:
            messages.error(request, 'Invalid credentials, please try again.')

    return render(request, 'login.html')



def register_user(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                firstname = request.POST.get('firstname')
                username = request.POST.get('username')
                email = request.POST.get('email')
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                college = request.POST.get('college')
                department = request.POST.get('department')
                course = request.POST.get('course')

                if password1 != password2:
                    messages.error(request, "Passwords do not match.")
                    return redirect('register')

                if User.objects.filter(username=username).exists():
                    messages.error(request, "Username already exists.")
                    return redirect('register')

                if User.objects.filter(email=email).exists():
                    messages.error(request, "Email is already registered.")
                    return redirect('register')

                user = User.objects.create_user(username=username, email=email, password=password1)
                user.is_active = False  
                user.save()

                Profile.objects.update_or_create(user=user, college=college, department=department, course=course)

                messages.success(request, "Your account has been created. Await admin approval.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Error creating profile: {str(e)}")
            return redirect('register')

    messages.get_messages(request).used = True  # Clears previous messages
    return render(request, 'register.html')


def register_students(request):
    return render(request, 'register_students.html', {})

def get_registered_students(request):
    """Fetch registered students from both Student and ScannedData models and return as JSON."""
    try:
        # Fetch all students from the Student model associated with the current user
        student_model_data = Student.objects.filter(user=request.user).values('student_id', 'name')

        # Fetch all students from the ScannedData model associated with the current user
        scanned_data_model_data = ScannedData.objects.filter(user=request.user).values('content')

        # Combine both datasets (student_id and name from Student, content from ScannedData)
        combined_data = []

        # Add students from the Student model
        for student in student_model_data:
            combined_data.append({'student_id': student['student_id'], 'name': student['name']})

        # Add students from ScannedData model, if they are not already in the combined_data list
        for scanned in scanned_data_model_data:
            if not any(student['student_id'] == scanned['content'] for student in combined_data):
                combined_data.append({'student_id': scanned['content'], 'name': scanned['content']})

        # Return the combined and deduplicated list of students
        return JsonResponse({"success": True, "students": combined_data})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out...')
    return redirect('login')


def save_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Fetch the user's profile details
            profile = Profile.objects.get(user=request.user)
            print(profile)

            for item in data.get('scannedData', []):
                content = item.get('content')
                ScannedData.objects.create(
                    content=content,
                    user=request.user,
                    college=profile.college,
                    department=profile.department,
                    course=profile.course
                )
            return JsonResponse({'success': True})
        except Profile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User profile not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def registered_students_view(request):
    """Render the registered students page."""
    return render(request, 'registered_students.html')

@csrf_exempt 
@login_required  
def delete_student(request, student_id):
    """Delete a student from all relevant models (ScannedData, Student, Attendance)."""
    if request.method == 'POST':
        try:
            decoded_student_id = urllib.parse.unquote(student_id)  # Decode the student ID
            print(f"Attempting to delete student with ID: {decoded_student_id}")

            # Delete from Attendance model first
            Attendance.objects.filter(student__student_id=decoded_student_id, user=request.user).delete()

            # Delete from ScannedData
            ScannedData.objects.filter(content=decoded_student_id, user=request.user).delete()

            # Delete from Student model
            Student.objects.filter(student_id=decoded_student_id, user=request.user).delete()

            return JsonResponse({"success": True})
        except Exception as e:
            print(f"Error deleting student: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

def save_selection(request):
    if request.method == "POST":
        year = request.POST.get('year')
        semester = request.POST.get('semester')

        # Ensure the user is logged in (assuming you're using authentication)
        if request.user.is_authenticated:
            user = request.user
        else:
            return redirect('login')

        # Check if this year and semester combination already exists for the user
        if YearRecord.objects.filter(year=year, semester=semester, user=user).exists():
            # If exists, return with an error message
            return render(request, 'year_semester_select.html', {
                'error': "This Year & Semester combination already exists.",
                'year_records': YearRecord.objects.filter(user=user)
            })

        # Save the year and semester record for the user
        YearRecord.objects.create(year=year, semester=semester, user=user)

        return redirect('year_semester_page')  # Redirect to the same page after saving

    # Fetch all YearRecords for the logged-in user
    year_records = YearRecord.objects.filter(user=request.user)

    return render(request, 'year_semester_select.html', {'year_records': year_records})

def delete_record(request, record_id):
    # Get the specific YearRecord to delete
    record = get_object_or_404(YearRecord, id=record_id, user=request.user)
    record.delete()  # Delete the record

    # Redirect back to the year and semester selection page after deletion
    return redirect('year_semester_page')

def units_page(request, year, semester):
    if request.method == 'POST' and request.user.is_authenticated:
        unit_name = request.POST.get('unit_name')

        if unit_name:
            year_record = YearRecord.objects.get(year=year, semester=semester, user=request.user)
            
            existing_unit = Unit.objects.filter(name=unit_name, year_record=year_record, user=request.user).first()
            
            if not existing_unit:
                Unit.objects.create(name=unit_name, year_record=year_record, user=request.user)
                messages.success(request, f'Unit "{unit_name}" has been added successfully.')
            else:
                messages.error(request, f'This unit "{unit_name}" has already been saved.')
            
            print(messages.get_messages(request))  # Debugging messages
            
            return redirect('units_page', year=year, semester=semester)  # Redirect to the same page after saving

    # Fetch the YearRecord for the logged-in user
    year_record = get_object_or_404(YearRecord, year=year, semester=semester, user=request.user)
    units = Unit.objects.filter(user=request.user, year_record=year_record)

    return render(request, 'units_page.html', {'units': units, 'year': year, 'semester': semester}) 


def delete_unit(request, unit_id):
    if request.method == 'POST' and request.user.is_authenticated:
        unit = get_object_or_404(Unit, id=unit_id, user=request.user)
        unit.delete()
        # Redirect back to the units page of the same year and semester
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



def select_lectures(request):

    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        if unit_id:
            unit = get_object_or_404(Unit, id=unit_id, user=request.user)
            
            # Retrieve the year and semester from the associated YearRecord
            year_record = unit.year_record
            year = year_record.year
            semester = year_record.semester
            
            # Dynamically create lectures for the unit
            for i in range(1, 15):  # 1 to 14 inclusive
                try:
                    Lecture.objects.get_or_create(
                        name=f"Lecture {i}",
                        unit=unit,
                        user=request.user
                    )
                except IntegrityError:
                    pass  # Handle errors if needed

    # Fetch all lectures for the unit
    lectures = Lecture.objects.filter(unit=unit)
    
    # Pass year and semester to the template
    return render(request, 'select_lectures.html', {
        'unit': unit,
        'lectures': lectures,
        'year': year,
        'semester': semester,
        'year_record': year_record
    })


@cache_control(no_cache=True, must_revalidate=True)
def get_data(request):
    """Fetch unique scanned students' data and return as JSON."""
    if request.method == 'GET' and request.user.is_authenticated:
        # Fetch only distinct student entries
        data = (
            ScannedData.objects.filter(user=request.user)
            .values('content')  # Group by student content
            .annotate(count=Count('id'))  # Count occurrences to track duplicates
            .order_by('content')  # Order for consistency
        )

        return JsonResponse({'success': True, 'data': list(data)})


def save_attendance(request):

    if request.method == "POST":
        try:
            # Parse JSON payload
            import json
            attendance_data = json.loads(request.body)
            lecture_id = attendance_data.get('lecture_id')
            unit_name = attendance_data.get('unitName')
            year_record_id = attendance_data.get('year_record')  # Get the ID
            attendance_entries = attendance_data.get('attendance_entries', [])
            user = request.user

            # Validate required fields
            if not all([lecture_id, unit_name, year_record_id]):
                return JsonResponse({"success": False, "error": "Missing required fields."})

            # Fetch the lecture, unit, and year record
            lecture = get_object_or_404(Lecture, id=lecture_id, user=request.user)
            unit = get_object_or_404(Unit, name=unit_name, user=request.user)
            year_record = get_object_or_404(YearRecord, id=year_record_id, user=request.user)  # Fetch year_record

            if Attendance.objects.filter(lecture=lecture).exists():
                return JsonResponse({"success": False, "error": "Attendance for this lecture has already been recorded."})


            # Save attendance for each student
            for entry in attendance_entries:
                student_id = entry.get('student_id')
                is_present = entry.get('is_present', False)

                # Get or create the student
                student, created = Student.objects.update_or_create(
                    student_id=student_id,
                    defaults={'name': student_id, 'user': user}
                )
                print(f"Student: {student}")

                # Save or update attendance record
                Attendance.objects.update_or_create(
                    user=request.user,
                    lecture=lecture,
                    student=student,
                    year_record=year_record,  # Assign the correct object
                    defaults={"is_present": is_present}
                )
                print(f"Attendance : {Attendance}")

            return JsonResponse({'success': True, 'message': 'Attendance saved successfully'})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})


def fetch_saved_attendance(request):
    """
    Fetch attendance data to populate a single table with lectures as columns.
    Data is fetched directly from the Attendance model, filtered by the selected unit name.
    """
    try:
        user = request.user
        # Get the selected unit name from the request
        unit_name = request.GET.get('unit_name')
        year_record = request.GET.get('year_record')
        if not unit_name:
            return JsonResponse({'success': False, 'error': 'Unit name is required.'})

        # Fetch all lectures for the selected unit
        lectures = Lecture.objects.filter(unit__name=unit_name, unit__user=user).order_by('id')

        # Fetch all attendance records for the selected unit
        attendances = Attendance.objects.filter(
            user=user,
            lecture__unit__name=unit_name,
            year_record_id=year_record,
            lecture__unit__user=user
        ).select_related('student', 'lecture')

        # Extract student data
        students = {}
        all_lecture_names = [lecture.name for lecture in lectures]  # Get all lecture names in order

        for attendance in attendances:
            student_id = attendance.student.student_id
            student_name = attendance.student.name
            lecture_name = attendance.lecture.name
            is_present = attendance.is_present

            # Ensure student record exists
            if student_id not in students:
                students[student_id] = {
                    'student_id': student_id,
                    'student_name': student_name,
                    'lectures': {lec: '' for lec in all_lecture_names}  # Initialize with empty values
                }

            # Update the lecture status
            students[student_id]['lectures'][lecture_name] = 'Present' if is_present else 'Absent'

        # Convert student dictionary to a list
        attendance_data = list(students.values())

        return JsonResponse({
            'success': True,
            'students': attendance_data,
            'lectures': all_lecture_names
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def year_semester_list(request):
    year_semesters = YearRecord.objects.filter(user=request.user)
    return render(request, 'year_semester_list.html', {'year_semesters': year_semesters})


def attendance_page(request, year_id, semester_id):
    # Get the YearRecord for the logged-in user
    year_record = get_object_or_404(YearRecord, year=year_id, semester=semester_id, user=request.user)

    # Fetch units related to the year and semester
    units = Unit.objects.filter(year_record=year_record, user=request.user)

    # Organize attendance data
    attendance_data = {}

    for unit in units:
        lectures = Lecture.objects.filter(unit=unit)
        lecture_names = [lecture.name for lecture in lectures]

        students = []
        student_ids = set()

        # Fetch attendance records linked to these lectures
        attendance_records = Attendance.objects.filter(
            lecture__in=lectures,
            year_record=year_record,
            user=request.user
        ).select_related('student', 'lecture')

        # First pass: Collect unique students
        for record in attendance_records:
            if record.student.student_id not in student_ids:
                student_ids.add(record.student.student_id)
                students.append({
                    'id': record.student.student_id,
                    'name': record.student.name,
                    'attendance': {lecture.name: '' for lecture in lectures}  # Default all to empty
                })

        # Second pass: Populate attendance status
        for record in attendance_records:
            for student in students:
                if student['id'] == record.student.student_id:
                    student['attendance'][record.lecture.name] = 'Present' if record.is_present else 'Absent'

        attendance_data[unit.name] = {
            'lectures': lecture_names,
            'students': students
        }

    return render(request, 'attendance_page.html', {
        'units': units,
        'year_record': year_record,
        'attendances': attendance_data
    })


def dashboard(request):
    selected_combination = request.GET.get("year_semester")  
    year_records = YearRecord.objects.filter(user=request.user).order_by("year", "semester")

    # Parse selected year and semester
    selected_year, selected_semester = None, None
    if selected_combination:
        try:
            selected_year, selected_semester = map(int, selected_combination.split("-"))
        except ValueError:
            selected_year, selected_semester = None, None  # Handle invalid values

    # If no valid selection or selection not found, default to the first available year/semester
    if not selected_year or not selected_semester or not year_records.filter(year=selected_year, semester=selected_semester).exists():
        if year_records.exists():
            first_record = year_records.first()
            selected_year = first_record.year
            selected_semester = first_record.semester

    # Fetch students from Attendance records instead of Student model
    student_ids = Attendance.objects.filter(
        year_record__year=selected_year,
        year_record__semester=selected_semester,
        user=request.user
    ).values_list("student_id", flat=True).distinct()

    students = Student.objects.filter(id__in=student_ids)
    students_count = students.count()

    # Fetch units for the selected year & semester
    units = Unit.objects.filter(
        year_record__year=selected_year,
        year_record__semester=selected_semester,
        user=request.user
    )
    total_units = units.count()
    # Calculate progress for each unit
    unit_progress = []
    for unit in units:
        total_lectures = unit.lectures.count()
        completed_lectures = Attendance.objects.filter(
            lecture__unit=unit
        ).values('lecture').distinct().count()  # Count distinct lectures where attendance was recorded
        
        progress_percentage = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
        unit_progress.append({"name": unit.name, "progress": progress_percentage})

    context = {
        "year_records": year_records,
        "selected_year": selected_year,
        "selected_semester": selected_semester,
        "students_count": students_count,
        "students": students,
        "total_units": total_units,
        "unit_progress": unit_progress,
    }
    return render(request, "dashboard.html", context)


def student_progress(request, student_id):
    selected_combination = request.GET.get("year_semester")  # Get "1-2" format

    # Parse selected year and semester
    selected_year, selected_semester = None, None
    if selected_combination:
        try:
            selected_year, selected_semester = map(int, selected_combination.split("-"))
        except ValueError:
            return JsonResponse({"error": "Invalid year/semester selection"}, status=400)

    # Fetch student or return 404 if not found
    student = get_object_or_404(Student, id=student_id, user=request.user)
    print(f'Student: {student}')

    # Get distinct units where attendance has been taken
    attended_units = Attendance.objects.filter(
        student=student,
        year_record__year=selected_year,
        year_record__semester=selected_semester,
        user=request.user
    ).values_list("lecture__unit", flat=True).distinct()



    unit_attendance = []
    for unit_id in attended_units:
        unit = Unit.objects.filter(id=unit_id, user=request.user).first()
        if not unit:
            continue  # Skip if unit not found

        # Count only lectures where attendance was recorded
        completed_lectures = Attendance.objects.filter(
            lecture__unit=unit
        ).values("lecture").distinct().count()

        attended_lectures = Attendance.objects.filter(
            student=student, lecture__unit=unit, is_present=True
        ).values("lecture").distinct().count()

        missed_lectures = max(0, completed_lectures - attended_lectures)

        unit_attendance.append({
            "name": unit.name,
            "attended": attended_lectures,
            "missed": missed_lectures,
        })

    return JsonResponse({
        "student_name": student.name,
        "units": unit_attendance
    })
