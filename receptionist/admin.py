from django.contrib import admin
from .models import Announcement

# Register your models here.
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("id", "date_announcement", "subject", "message", "posted_by")
    list_editable = ("subject", "message", "posted_by", )
    list_display_links = ("id", )
    search_fields = ("subject", )
    list_filter = ("posted_by", )
