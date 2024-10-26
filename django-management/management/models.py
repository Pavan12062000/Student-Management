from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models 

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)  # Ensures unique email addresses
    date_of_birth = models.DateField()
    enrollment_date = models.DateField()
    grade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])  # Ensures grade is between 1 and 12
