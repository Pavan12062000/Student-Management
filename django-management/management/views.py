import json
from django.shortcuts import render, get_object_or_404, redirect
from .models import Student
from .forms import StudentForm  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q  # Import Q for complex queries
from django.core.paginator import Paginator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime


# Display a list of all students
def student_list(request):
    # Get the search query from the request
    query = request.GET.get('q', '')

    # Get the selected year from the dropdown, default is the current year
    selected_year = request.GET.get('selected_year', '')

    # Get the number of records per page from the request, default is 10
    try:
        records_per_page = int(request.GET.get('records_per_page', 10))
        # Ensure records_per_page is in the allowed options
        if records_per_page not in [1, 5, 10, 15, 20, 25]:
            records_per_page = 10
    except ValueError:
        records_per_page = 10

    # Filter students based on search query
    students = Student.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query)
    ) if query else Student.objects.all()

        # Filter students based on selected year
    if selected_year:
        try:
            selected_year = int(selected_year)  # Convert to int only if it's not empty
            students_for_year = students.filter(enrollment_date__year=selected_year)
        except ValueError:
            students_for_year = students  # If there's an error in conversion, show all
    else:
        students_for_year = students  # Show all students if "All Years" is selected

    # Paginate the students queryset
    paginator = Paginator(students_for_year, records_per_page)  # Paginate based on the filtered list
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get available years for dropdown
    available_years = Student.objects.dates('enrollment_date', 'year').distinct()

    # Filter data analytics based on the selected year
    jan_apr_count = students_for_year.filter(enrollment_date__month__in=[1, 2, 3, 4]).count()
    may_aug_count = students_for_year.filter(enrollment_date__month__in=[5, 6, 7, 8]).count()
    sep_dec_count = students_for_year.filter(enrollment_date__month__in=[9, 10, 11, 12]).count()

    # Graph data: Enrollment trend over months for the selected year
    graph_labels = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    graph_data = [
        students_for_year.filter(enrollment_date__month=month).count()
        for month in range(1, 13)
    ]

    # Prepare JSON data for JavaScript
    enrollment_data = json.dumps({
        'pieChartData': [jan_apr_count, may_aug_count, sep_dec_count],
        'graphLabels': graph_labels,
        'graphData': graph_data
    })

    # Render the student list template
    return render(request, 'management/student_list.html', {
        'page_obj': page_obj,
        'query': query,
        'records_per_page': records_per_page,
        'records_per_page_options': [1, 5, 10, 15, 20, 25],
        'available_years': available_years,
        'selected_year': selected_year,
        'enrollment_data': enrollment_data,
    })

# Display the details of a single student
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'management/student_detail.html', {'student': student})


# Add a new student
# @login_required
def student_create(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to add a new student.')
        return redirect('login')
    else:
        if request.method == "POST":
            form = StudentForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Student has been created successfully!')
                return redirect('student_list')
            else:
                messages.error(request, 'There was an error creating the student. Please correct the form below.')
        else:
            form = StudentForm()
        return render(request, 'management/student_form.html', {'form': form})


# Edit an existing student's information
# @login_required
def student_edit(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to edit an existing student.')
        return redirect('login')
    else:
        student = get_object_or_404(Student, pk=pk)
        if request.method == "POST":
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                messages.success(request, 'Student information has been updated successfully!')
                return redirect('student_detail', pk=student.pk)
            else:
                messages.error(request, 'There was an error updating the student. Please correct the form below.')
        else:
            form = StudentForm(instance=student)
        return render(request, 'management/student_form.html', {'form': form})


# Delete an existing student
# @login_required
def student_delete(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to delete an existing student.')
        return redirect('login')
    else:
        student = get_object_or_404(Student, pk=pk)
        if request.method == "POST":
            student.delete()
            messages.success(request, 'Student has been deleted successfully!')
            return redirect('student_list')  # Redirect to the student list after deletion
        return render(request, 'management/student_detail.html', {'student': student})


# Register a new user
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! Please log in.')
            return redirect('login')  # Redirect to the login page after successful registration
        else:
            messages.error(request, 'There was an error creating your account. Please correct the form below.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


# User login view
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You are now logged in!')
                return redirect('student_list')  # Redirect to student list after login
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


# Forgot password view
def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if the user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Username does not exist.')
            return redirect('forgot_password')

        # Validate the new password
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('forgot_password')

        # Use Django's built-in password validation
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return redirect('forgot_password')

        # Set the new password and save
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Your password has been successfully updated! Please log in with your new password.')
        return redirect('login')  # Redirect to the login page after successful password update
        
    return render(request, 'registration/forgot_password.html')

# User logout view
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')  # Redirect to the login page after logout
