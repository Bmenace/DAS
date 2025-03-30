from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    college = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    course = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username


class ScannedData(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanned_data')
    college = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        """ Automatically populate college, department, and course from the user's profile """
        if not self.college or not self.department or not self.course:
            try:
                profile = Profile.objects.get(user=self.user)
                self.college = profile.college
                self.department = profile.department
                self.course = profile.course
            except Profile.DoesNotExist:
                pass  # Handle cases where profile is missing
        super().save(*args, **kwargs)

    def __str__(self):
        return self.content


class Student(models.Model):
    student_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')


class YearRecord(models.Model):
    YEAR_CHOICES = [
        (1, 'Year 1'),
        (2, 'Year 2'),
        (3, 'Year 3'),
        (4, 'Year 4'),
        (5, 'Year 5'),
        (6, 'Year 6'),
    ]

    SEMESTER_CHOICES = [
        (1, 'Semester 1'),
        (2, 'Semester 2'),
        (3, 'Semester 3'),
    ]

    year = models.IntegerField(choices=YEAR_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('year', 'semester', 'user')


    def __str__(self):
        return f"Year {self.year}, Semester {self.semester}"


class Unit(models.Model):
    name = models.CharField(max_length=255)
    year_record = models.ForeignKey(YearRecord, on_delete=models.CASCADE)  # Link to YearRecord
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Lecture(models.Model):
    name = models.CharField(max_length=100)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lectures')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lectures')

    def __str__(self):
        return f"{self.name} - {self.unit.name}"



class Attendance(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    is_present = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    year_record = models.ForeignKey(YearRecord, on_delete=models.CASCADE, related_name='attendances')

    def __str__(self):
        return f"{self.student.name} - {self.lecture.name} - {'Present' if self.is_present else 'Absent'}"
