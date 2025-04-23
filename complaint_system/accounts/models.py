from django.contrib.auth.models import AbstractUser
from django.db import models

SUPER_ADMIN = 'Super Admin'
ADMIN = 'Admin'
USER = 'User'

INCHARGE = 'In Charge'
STAFF = 'Staff'


# Role Choices.
ROLE_CHOICES = (
    (SUPER_ADMIN, 'super admin'),
    (ADMIN, 'admin'),
    (USER, 'user'),
)

# Designation Choices.
DESIGNATION_CHOICES = [
    (INCHARGE, 'incharge'),
    (STAFF, 'staff'),
]

# Department Model.
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# User Model.
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=25, choices=DESIGNATION_CHOICES, default='staff')
    