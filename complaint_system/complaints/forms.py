from django import forms
from .models import Complaint, ComplaintType, ReassignedComplaint, ComplaintRemarks
from accounts.models import CustomUser, Department
from django.db.models import Count, Q

# Complaint Form.
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['department', 'complaint_type', 'location', 'description']
        labels = {
            'department': 'Concern Department'
        }

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'cols': 20  
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(ComplaintForm, self).__init__(*args, **kwargs)

        self.fields['department'].queryset = Department.objects.annotate(
            valid_complaint_type_count=Count(
                'complaint_types',
                filter=~Q(complaint_types__name__iexact='Others')
            )
        ).filter(valid_complaint_type_count__gt=0)

        self.fields['complaint_type'].queryset = ComplaintType.objects.none()

        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['complaint_type'].queryset = ComplaintType.objects.filter(department_id=department_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['complaint_type'].queryset = ComplaintType.objects.filter(department=self.instance.department)

# Reassigned Form
class ReassignedForm(forms.ModelForm):

    class Meta:
        model = ReassignedComplaint
        fields = ['reassigned_to']
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            user_department = getattr(self.request.user, 'department', None)

            if user_department:
                self.fields['reassigned_to'].queryset = CustomUser.objects.filter(department=user_department).exclude(id=self.request.user.id)
            else:
                self.fields['reassigned_to'].queryset = CustomUser.objects.none()

# Remark Form.
class RemarkForm(forms.ModelForm):
    class Meta:
        model = ComplaintRemarks
        fields = ['remarks']  

        widgets = {
            'remarks': forms.Textarea(attrs={
                'rows': 3, 
                'cols': 20  
            }),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request:
            user_department = getattr(self.request.user, 'department', None)

            if user_department:
                self.fields['complaint'].queryset = Complaint.objects.filter(department=user_department)
            else:
                self.fields['complaint'].queryset = Complaint.objects.none()
