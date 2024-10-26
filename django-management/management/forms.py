from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'enrollment_date', 'grade']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        student_id = self.instance.pk  # Get the current student's ID

        # Check if the email exists for another student
        if Student.objects.filter(email=email).exclude(pk=student_id).exists():
            raise forms.ValidationError("A student with this email already exists.")
        
        if not email or "@" not in email:
            raise forms.ValidationError("Please enter a valid email address.")

        return email


    def clean_grade(self): #extra level of validation for grades
        grade = self.cleaned_data.get('grade')
        if not (1 <= grade <= 12):
            raise forms.ValidationError("Grade must be between 1 and 12.")
        return grade
    
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['date_of_birth'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['enrollment_date'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['grade'].widget.attrs['placeholder'] = 'Enter grade (1-12)'