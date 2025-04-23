from django.db import models
from accounts.models import CustomUser, Department

# Predefine Complaint Model.
class ComplaintType(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='complaint_types')

    def __str__(self):
        return self.name
    
# Location Model.
class Location(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Status Choices.
STATUS_CHOICES = (
    ('open', 'Open'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('cancelled', 'Cancelled'),
)

# Complaint Model.
class Complaint(models.Model):
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    location = models.ForeignKey(Location, related_name='complaint_locations', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_by = models.ForeignKey(CustomUser, related_name='created_complaints', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, related_name='assigned_complaints', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.complaint_type)

# Complaint History Model.
class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    status_changed_to = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='changed_complaints')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.complaint.complaint_type)

# Reassigned Complaint Model
class ReassignedComplaint(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    reassigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='reassign_complaints')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reassigned_to)

# Remark Model
class ComplaintRemarks(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    remarks = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='created_remark')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.remarks
    