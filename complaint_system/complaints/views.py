from django.shortcuts import render, redirect, get_object_or_404
from .forms import ComplaintForm, ReassignedForm, RemarkForm
from accounts.models import CustomUser
from .models import Complaint, ComplaintHistory, ComplaintType, ComplaintRemarks
from accounts.models import Department
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

# views.py
def load_complaint_types(request):
    department_id = request.GET.get('department')
    complaint_types = ComplaintType.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(complaint_types.values('id', 'name')), safe=False)

# Complaints View.
def ComplaintView(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)

        if form.is_valid():
            new_complaint = form.save(commit=False)
            new_complaint.created_by = request.user
            department = form.cleaned_data.get('department')
            complaint_type = form.cleaned_data.get('complaint_type')
            if not complaint_type:
                types = ComplaintType.objects.filter(department=department)
                if types.count() == 1:
                    form.instance.complaint_type = types.first()
                elif types.count() > 1:
                    form.add_error('complaint_type', 'Please select a complaint type.')
                    return render(request, 'complaints.html', {'form': form})
            assigned_user = CustomUser.objects.filter(department=department, role='Admin').first()
            if assigned_user:
                new_complaint.assigned_to = assigned_user
            new_complaint.save()

            ComplaintHistory.objects.create(
                complaint=new_complaint,
                status_changed_to = new_complaint.status,
                changed_by = new_complaint.created_by,
            )
            return redirect('staff')
    else:
        form = ComplaintForm()

    context = {
        'form': form
    }

    return render(request, 'complaints.html', context)

# All Complaints View
def AllComplaintsView(request):
    user = request.user
    complaints = ComplaintHistory.objects.filter(complaint__created_by = user).order_by('complaint__created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'all_complaints.html', context)

# Assigned Complaint View.
def AssignedComplaint(request):
    user = request.user
    complaints = ComplaintHistory.objects.filter(
        Q(complaint__assigned_to=user) | 
        Q(complaint__department=user.department)
        ).order_by('complaint__created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'assigned_complaint.html', context)

# Assigned Complaint Details View.
def AssignedComplaintDetails(request, id):
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)

    context = {
        'complaint': complaint,
        'remarks': remark
    }
    return render(request, 'assigned_complaint_details.html', context)

# Staff Update Complaint Status View.
def StaffUpdateComplaintStatus(request, id):
    complaint = get_object_or_404(ComplaintHistory, id=id)

    if complaint.complaint.assigned_to != request.user:
        return redirect('staff_assigned_tasks')
    
    if complaint.complaint.status in ['Closed', 'Cancelled']:
        messages.warning(request, f"Cannot update status. Complaint is already {complaint.complaint.status}.")
        return redirect('staff_assigned_tasks')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Closed' and complaint.status_changed_to == 'Cancelled':
            messages.warning(request, "Cancelled complaint cannot be Closed.")
        else:
            complaint.changed_by = request.user
            complaint.status_changed_to = new_status
            complaint.save()
            
            complaint.complaint.status = new_status
            complaint.complaint.save()

            messages.success(request, "Status updated successfully.")

    return redirect('staff_assigned_tasks')

# Admin Update Complaint Status View.
def AdminUpdateComplaintStatus(request, id):
    complaint = get_object_or_404(ComplaintHistory, id=id)

    if complaint.complaint.assigned_to != request.user:
        return redirect('assigned_complaint')
    
    if complaint.complaint.status in ['Closed', 'Cancelled']:
        messages.warning(request, f"Cannot update status. Complaint is already {complaint.complaint.status}.")
        return redirect('assigned_complaint')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Closed' and complaint.status_changed_to == 'Cancelled':
            messages.warning(request, "Cancelled complaint cannot be Closed.")
        else:
            complaint.changed_by = request.user
            complaint.status_changed_to = new_status
            complaint.save()
            
            complaint.complaint.status = new_status
            complaint.complaint.save()

            messages.success(request, "Status updated successfully.")

    return redirect('assigned_complaint')

# Cancel Complaint View.
def CancelComplaint(request, id):
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)

    if complaint.complaint.created_by != request.user:
        return redirect('staff_complaints_history')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'Cancelled' and complaint.complaint.status == 'Closed':
            messages.warning(request, "Closed complaint cannot be cancelled.")
        else:
            complaint.status_changed_to = new_status
            complaint.save()

            Complaint.objects.update(
                id = complaint.complaint_id,
                status = new_status,               
            )

            messages.success(request, "Status updated successfully.")

    return redirect('staff_complaints_history')

# Complaint Details View.
def ComplaintDetails(request, id):
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)
    
    context = {
        'complaint': complaint,
        'remarks': remark
    }
    
    return render(request, 'complaint_details.html', context)

# Complain History View.
def ComplainHistory(request):
    selected_department_id = request.GET.get('department')
    page_number = request.GET.get('page')

    if selected_department_id:
        all_complaints = ComplaintHistory.objects.filter(
            complaint__department_id=selected_department_id
        ).order_by('-complaint__created_at')
    else:
        all_complaints = ComplaintHistory.objects.all().order_by('-complaint__created_at')

    paginator = Paginator(all_complaints, 10)  
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'selected_department': int(selected_department_id) if selected_department_id else None,
    }

    return render(request, 'complaint_history.html', context)

# Reassigned Complaint View.
def ReassignedComplaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = ReassignedForm(request.POST, request=request)
        if form.is_valid():
            reassign_complaint = form.save(commit=False)
            reassign_complaint.complaint = complaint
            reassign_complaint.reassigned_to = form.cleaned_data['reassigned_to']
            reassign_complaint.save()

            reassign_complaint.complaint.assigned_to = reassign_complaint.reassigned_to
            reassign_complaint.complaint.save()


            return redirect('assigned_complaint_details', id=reassign_complaint.complaint.id)
    else:
        form = ReassignedForm(request=request)

    context = {
        'form': form
    }
    return render(request, 'reassigned_complaint.html', context)

# Assigned Tasks View.
def AssignedTasks(request):
    user = request.user
    assign_complaints = ComplaintHistory.objects.filter(complaint__assigned_to = user).order_by('complaint__created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(assign_complaints, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'assigned_tasks.html', context)

# Assigned Task Details
def AssignedTaskDetails(request, id):
    complaint = get_object_or_404(ComplaintHistory, complaint_id=id)
    remark = ComplaintRemarks.objects.filter(complaint_id=id)

    if complaint.complaint.assigned_to != request.user:
        return redirect('staff_assigned_tasks')
    
    context = {
        'task': complaint,
        'remarks': remark
    }
    return render(request, 'assigned_task_details.html', context)

# Complaint Remark View.
def RemarkComplaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = RemarkForm(request.POST)
        if form.is_valid():
            remark = form.save(commit=False)
            remark.complaint = complaint
            remark.remarks = form.cleaned_data.get('remarks')
            remark.created_by = request.user
            remark.save()

            if request.user.designation == 'Staff':
                return redirect('staff_assigned_tasks_details', id=complaint.id)
            else:
                return redirect('assigned_complaint_details', id=complaint.id)

    else:
        form = RemarkForm()
    context = {
        'form': form
    }
    return render(request, 'remark.html', context)
