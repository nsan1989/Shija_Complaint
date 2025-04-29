from django.urls import path
from .views import ComplaintView, AllComplaintsView, AssignedComplaint, StaffUpdateComplaintStatus, AdminUpdateComplaintStatus, CancelComplaint, load_complaint_types, ComplaintDetails, ComplainHistory, AssignedComplaintDetails, ReassignedComplaint, AssignedTasks, AssignedTaskDetails, RemarkComplaint

urlpatterns = [
    path('raised_complaints/', ComplaintView, name='complaints'),
    path('overall_complaint/', ComplainHistory, name='overall_complaint'),
    path('overall_complaint/<int:id>/complaint_details/', ComplaintDetails, name='overall_complaints_details'),
    path('staff/raised_complaints/', AllComplaintsView, name='staff_complaints_history'),
    path('staff/raised_complaints/<int:id>/complaint_details/', ComplaintDetails, name='staff_complaints_details'),
    path('staff/assigned_tasks/', AssignedTasks, name='staff_assigned_tasks'),
    path('staff/assigned_tasks/<int:id>/assigned_tasks_details/', AssignedTaskDetails, name='staff_assigned_tasks_details'),
    path('incharge/raised_complaints/', AllComplaintsView, name='incharge_complaints_history'),
    path('incharge/raised_complaints/<int:id>/complaint_details/', ComplaintDetails, name='incharge_complaints_details'),
    path('incharge/assigned_complaint/', AssignedComplaint, name='assigned_complaint'),
    path('incharge/assigned_complaint/<int:id>/assigned_complaint_details/', AssignedComplaintDetails, name='assigned_complaint_details'),
    path('incharge/assigned_complaint/<int:complaint_id>/assigned_complaint_details/reassign_complaints/', ReassignedComplaint, name='reassign_complaints'),
    path('complaints_remarks/<int:complaint_id>/remark/', RemarkComplaint, name='complaints_remarks'),
    path('staff_update_complaint_status/<int:id>/', StaffUpdateComplaintStatus, name='staff_update_complaint_status'),
    path('admin_update_complaint_status/<int:id>/', AdminUpdateComplaintStatus, name='admin_update_complaint_status'),
    path('cancel_complaint/<int:id>/', CancelComplaint, name='cancel_complaint'),
    path('ajax/load-complaint-types/', load_complaint_types, name='ajax_load_complaint_types'),
]