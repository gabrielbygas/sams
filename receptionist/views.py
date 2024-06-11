from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages
from receptionist.forms import AnnouncementForm
from receptionist.models import Announcement

# Create your views here.
@login_required
def home(request):
    user = request.user
    return render(request, "receptionist/home.html", {'user': user})

# Only if you are receptionist
def is_receptionist(user):
    return user.is_receptionist()

@login_required
def receptionist_error_page(request):
    context = {}
    if not request.user.is_superuser or request.user.is_receptionist():
        context['error_message'] = "You is not allowed to access this page."
    return render(request, "receptionist/receptionist_error_page.html", context)

# Announcement List
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_receptionist, login_url='receptionists:error-page'), name='dispatch')
class AnnouncementListView(ListView):
    model = Announcement
    context_object_name = "announcements"
    template_name = "receptionist/announcement_list.html"

    def get_queryset(self):
        return Announcement.objects.all().order_by('-date_announcement')
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest': #to specify an ajax request (copilot-Microsoft help)
            data = list(self.get_queryset().values(
                'id',
                'date_announcement', 
                'subject',
                'message', 
                'posted_by__user__first_name', 
                'posted_by__user__last_name'
            ))
            return JsonResponse(data, safe=False)
        else:
            return super().render_to_response(context, **response_kwargs)

# Announcement Detail
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_receptionist, login_url='receptionists:error-page'), name='dispatch')
class AnnouncementDetailView(DetailView):
    model = Announcement
    context_object_name = "announcement"
    template_name = "receptionist/announcement_detail.html"

# Announcement Create
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_receptionist, login_url='receptionists:error-page'), name='dispatch')
class AnnouncementCreateView(CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "receptionist/announcement_create.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'receptionist'): #if user is student
            form.instance.posted_by = user.receptionist
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Announcement created successfully!')
        return reverse("receptionists:list-announcement")

# Announcement Update
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_receptionist, login_url='receptionists:error-page'), name='dispatch')
class AnnouncementUpdateView(UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "receptionist/announcement_update.html"

    def form_valid(self, form):
        user = self.request.user
        if hasattr(user, 'receptionist'): #if user is student
            form.instance.posted_by = user.receptionist
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Announcement updated successfully!')
        return reverse("receptionists:list-announcement")
    
# Announcement Delete
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_receptionist, login_url='receptionists:error-page'), name='dispatch')
class AnnouncementDeleteView(DeleteView):
    model = Announcement
    context_object_name = "announcement"
    template_name = "receptionist/announcement_confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, 'Announcement deleted successfully!')
        return reverse("receptionists:list-announcement")