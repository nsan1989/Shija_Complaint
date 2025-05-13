from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Department, CustomUser
from complaints.models import Complaint, ComplaintHistory
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

# Register View.
def Register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            if user.designation == 'In Charge':
                user.role = 'Admin'
            else:
                user.role = 'User'
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            return redirect('login')
        else:
            messages.error(request, 'please enter valid details!') 
    else:
        form = RegisterForm()

    return render(request, 'register.html', {
        'form': form
    })

# Login View.
def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user.refresh_from_db()
                if user.role == 'Super Admin':
                    return redirect('super_admin')
                elif user.role == 'Admin':
                    return redirect('staff_admin')
                else:
                    return redirect('staff')
            else:
                messages.error(request, 'Invalid Credentials!')
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
    })

# Profile View.
def Profile(request):
    new_user = request.user
    path = request.path
    try:
        user_role = new_user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    
    if path.startswith('/staff/profile_details/') and user_role == 'User':
        return render(request, 'profile.html', {'user': new_user})
    if path.startswith('/incharge/profile_details/') and user_role == 'Admin':
        return render(request, 'profile.html', {'user': new_user})
    raise PermissionDenied("You are not authorized to view this page.")

# Department View
def DepartmentView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    department = Department.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(department, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'dept': page_obj,
    }
    if path.startswith('/super_admin/departments/') and user_role == 'Super Admin':
        return render(request, 'department.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Users View
def UsersView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except:
        raise PermissionDenied("User profile not found.")
    all_users = CustomUser.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(all_users, 10)  
    page_obj = paginator.get_page(page_number)
    context = {
        'all_users': page_obj
    }
    if path.startswith('/super_admin/all_users/') and user_role == 'Super Admin':
        return render(request, 'all_users.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

#Super Admin View
def SuperAdminView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    complaints = ComplaintHistory.objects.all().count()
    departments = Department.objects.all().count()
    users = CustomUser.objects.all().count()
    status_count = {
        'Open': Complaint.objects.filter(status='Open').count(),
        'In Progress': Complaint.objects.filter(status='In Progress').count(),
        'Resolved': Complaint.objects.filter(status='Resolved').count(),
        'Cancelled': Complaint.objects.filter(status='Cancelled').count()
    }
    color_map = {
    'Open': 'blue',
    'In Progress': 'green',
    'Resolved': 'yellow',
    'Cancelled': 'red',
    }
    labels = [status for status, count in status_count.items() if count > 0]
    values = [count for status, count in status_count.items() if count > 0]
    colors = [color_map[status] for status in labels]
    image_base64 = None
    if values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
    context = {
        'chart': image_base64,
        'complaints': complaints,
        'departments': departments,
        'users': users
    }
    if path.startswith('/super_admin/dashboard/') and user_role == 'Super Admin':
        return render(request, 'super_admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Admin View
def AdminView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    created_complaint = Complaint.objects.filter(created_by = user).count()
    # Created Complaint Chart
    created_status_count = {
        'Open': Complaint.objects.filter(created_by=user, status='Open').count(),
        'In Progress': Complaint.objects.filter(created_by=user, status='In Progress').count(),
        'Resolved': Complaint.objects.filter(created_by=user, status='Resolved').count(),
        'Cancelled': Complaint.objects.filter(created_by=user, status='Cancelled').count()
    }
    created_color_map = {
    'Open': 'blue',
    'In Progress': 'green',
    'Resolved': 'yellow',
    'Cancelled': 'red',
    }
    labels = [status for status, count in created_status_count.items() if count > 0]
    values = [count for status, count in created_status_count.items() if count > 0]
    colors = [created_color_map[status] for status in labels]
    created_image_base64 = None
    if values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        created_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
        
    assigned_complaint = Complaint.objects.filter(assigned_to = user).count()
    # Assigned Complaint Chart
    assign_status_count = {
        'Open': Complaint.objects.filter(assigned_to=user, status='Open').count(),
        'In Progress': Complaint.objects.filter(assigned_to=user, status='In Progress').count(),
        'Resolved': Complaint.objects.filter(assigned_to=user, status='Resolved').count(),
        'Cancelled': Complaint.objects.filter(assigned_to=user, status='Cancelled').count()
    }
    assign_color_map = {
    'Open': 'blue',
    'In Progress': 'green',
    'Resolved': 'yellow',
    'Cancelled': 'red',
    }
    labels = [status for status, count in assign_status_count.items() if count > 0]
    values = [count for status, count in assign_status_count.items() if count > 0]
    colors = [assign_color_map[status] for status in labels]
    assign_image_base64 = None
    if values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        assign_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)   
    context = {
        'created_complain': created_complaint,
        'assign_complain': assigned_complaint,
        'created_chart': created_image_base64,
        'assign_chart': assign_image_base64
    }

    if path.startswith('/incharge/dashboard/') and user_role == 'Admin':
        return render(request, 'admin_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")

# Staff View
def StaffView(request):
    user = request.user
    path = request.path
    try:
        user_role = user.role
    except AttributeError:
        raise PermissionDenied("User profile not found.")
    created_complaints = Complaint.objects.filter(created_by=user).count()
    assigned_complaints = Complaint.objects.filter(assigned_to=user).count()
    status_count = {
        'Open': Complaint.objects.filter(created_by=user, status='Open').count(),
        'In Progress': Complaint.objects.filter(created_by=user, status='In Progress').count(),
        'Resolved': Complaint.objects.filter(created_by=user, status='Resolved').count(),
        'Cancelled': Complaint.objects.filter(created_by=user, status='Cancelled').count()
    }
    color_map = {
    'Open': 'blue',
    'In Progress': 'green',
    'Resolved': 'yellow',
    'Cancelled': 'red',
    }
    labels = [status for status, count in status_count.items() if count > 0]
    values = [count for status, count in status_count.items() if count > 0]
    colors = [color_map[status] for status in labels]
    image_base64 = None
    if values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)
    # Assigned Complaint Chart
    assign_status_count = {
        'Open': Complaint.objects.filter(assigned_to=user, status='Open').count(),
        'In Progress': Complaint.objects.filter(assigned_to=user, status='In Progress').count(),
        'Resolved': Complaint.objects.filter(assigned_to=user, status='Resolved').count(),
        'Cancelled': Complaint.objects.filter(assigned_to=user, status='Cancelled').count()
    }
    assign_color_map = {
    'Open': 'blue',
    'In Progress': 'green',
    'Resolved': 'yellow',
    'Cancelled': 'red',
    }
    labels = [status for status, count in assign_status_count.items() if count > 0]
    values = [count for status, count in assign_status_count.items() if count > 0]
    colors = [assign_color_map[status] for status in labels]
    assign_image_base64 = None
    if values:
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        assign_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig) 
    context = {
        'complaints': created_complaints,
        'assign_complaints': assigned_complaints,
        'created_chart': image_base64,
        'assign_chart': assign_image_base64
    }
    if path.startswith('/staff/dashboard/') and user_role == 'User':
        return render(request, 'staff_dashboard.html', context)
    raise PermissionDenied("You are not authorized to view this page.")
