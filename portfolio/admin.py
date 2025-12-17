from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Profile, Project, Skill, Experience
from django import forms
import base64
from django.db.models.signals import post_save
from django.dispatch import receiver

# ========== SIGNALS TO AUTO-CREATE PROFILE ==========
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

# ========== INLINE PROFILE FOR USER ADMIN ==========
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('title', 'bio', 'email', 'phone', 'location',
              'profile_image_preview', 'github', 'linkedin', 
              'twitter', 'facebook')
    readonly_fields = ('profile_image_preview',)
    
    def profile_image_preview(self, obj):
        if obj.profile_image_url:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius: 10px; object-fit: cover;" /><br>'
                '<small>Base64 Image ({})</small>',
                obj.profile_image_url,
                obj.profile_image_format or 'Unknown'
            )
        return "No image"
    profile_image_preview.short_description = 'Profile Image'

# ========== CUSTOM USER ADMIN ==========
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_profile_title')
    
    def get_profile_title(self, obj):
        try:
            return obj.profile.title
        except:
            return 'No Profile'
    get_profile_title.short_description = 'Profile Title'

# ========== PROFILE ADMIN ==========
class ProfileAdminForm(forms.ModelForm):
    profile_image_upload = forms.ImageField(
        required=False,
        label="Upload Profile Image",
        help_text="Select an image to upload (will be stored as base64)"
    )
    
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'profile_image_base64': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = ('user', 'title', 'email', 'phone', 'location', 'profile_image_preview')
    search_fields = ('user__username', 'title', 'email', 'location')
    list_filter = ('user__is_staff', 'user__is_active')
    readonly_fields = ('profile_image_preview',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'title', 'bio', 'email', 'phone', 'location')
        }),
        ('Profile Image', {
            'fields': ('profile_image_upload', 'profile_image_preview'),
            'description': 'Upload image - it will be converted to base64 and stored in database'
        }),
        ('Social Links', {
            'fields': ('github', 'linkedin', 'twitter', 'facebook'),
        }),
        ('Advanced (Optional)', {
            'classes': ('collapse',),
            'fields': ('profile_image_base64', 'profile_image_format'),
        }),
    )
    
    def profile_image_preview(self, obj):
        if obj.profile_image_url:
            return format_html(
                '<img src="{}" width="150" height="150" style="border-radius: 10px; object-fit: cover;" /><br>'
                '<small>Format: {} | Base64 length: {} chars</small>',
                obj.profile_image_url,
                obj.profile_image_format or 'Unknown',
                len(obj.profile_image_base64 or '')
            )
        return "No image uploaded"
    profile_image_preview.short_description = 'Current Image'
    
    def save_model(self, request, obj, form, change):
        # Handle image upload
        uploaded_image = form.cleaned_data.get('profile_image_upload')
        if uploaded_image:
            obj.set_profile_image(uploaded_image)
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Show all users in dropdown
            kwargs["queryset"] = User.objects.all().order_by('username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== PROJECT ADMIN ==========
class ProjectAdminForm(forms.ModelForm):
    image_upload = forms.ImageField(
        required=False,
        label="Upload Project Image",
        help_text="Select project image (will be stored as base64)"
    )
    
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'image_base64': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom queryset for profile field
        if 'profile' in self.fields:
            self.fields['profile'].queryset = Profile.objects.all().order_by('user__username')
            # Custom display text for dropdown
            self.fields['profile'].label_from_instance = lambda obj: f"{obj.user.username} (ID: {obj.id}) - {obj.title}"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm
    list_display = ('title', 'get_profile_display', 'featured', 'created_at', 'image_preview')
    list_filter = ('featured', 'created_at', 'profile__user__username')
    search_fields = ('title', 'technologies', 'description', 'profile__user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('image_preview',)
    
    # এইটা খুবই গুরুত্বপূর্ণ: raw_id_fields ব্যাবহার করবে না
    # raw_id_fields = ('profile',)  # এই লাইন থাকলে ডিলিট করো
    
    fieldsets = (
        ('Project Info', {
            'fields': ('profile', 'title', 'description', 'technologies')
        }),
        ('Project Image', {
            'fields': ('image_upload', 'image_preview'),
        }),
        ('Links & Status', {
            'fields': ('github_link', 'live_link', 'featured')
        }),
        ('Advanced (Optional)', {
            'classes': ('collapse',),
            'fields': ('image_base64', 'image_format'),
        }),
    )
    
    def get_profile_display(self, obj):
        if obj.profile:
            return f"{obj.profile.user.username} (ID: {obj.profile.id})"
        return "No Profile"
    get_profile_display.short_description = 'Profile (User - ID)'
    get_profile_display.admin_order_field = 'profile__user__username'
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" width="200" style="border-radius: 10px; max-height: 150px; object-fit: cover;" /><br>'
                '<small>Format: {} | Base64 length: {} chars</small>',
                obj.image_url,
                obj.image_format or 'Unknown',
                len(obj.image_base64 or '')
            )
        return "No image uploaded"
    image_preview.short_description = 'Preview'
    
    def save_model(self, request, obj, form, change):
        # Handle project image upload
        uploaded_image = form.cleaned_data.get('image_upload')
        if uploaded_image:
            obj.set_image(uploaded_image)
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile__user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Customize profile field to show all profiles with user info
        if db_field.name == "profile":
            kwargs["queryset"] = Profile.objects.all().select_related('user').order_by('user__username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== SKILL ADMIN ==========
class SkillAdminForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'profile' in self.fields:
            self.fields['profile'].queryset = Profile.objects.all().order_by('user__username')
            self.fields['profile'].label_from_instance = lambda obj: f"{obj.user.username} (ID: {obj.id})"

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    form = SkillAdminForm
    list_display = ('name', 'category', 'percentage', 'get_profile_display', 'color_preview')
    list_filter = ('category', 'profile__user__username')
    search_fields = ('name', 'profile__user__username')
    
    # raw_id_fields ব্যবহার করবে না
    # raw_id_fields = ('profile',)  # এই লাইন থাকলে ডিলিট করো
    
    fieldsets = (
        ('Skill Info', {
            'fields': ('profile', 'name', 'category', 'percentage')
        }),
        ('Display Settings', {
            'fields': ('color', 'color_preview'),
        }),
    )
    
    readonly_fields = ('color_preview',)
    
    def get_profile_display(self, obj):
        if obj.profile:
            return f"{obj.profile.user.username} (ID: {obj.profile.id})"
        return "No Profile"
    get_profile_display.short_description = 'Profile'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 50px; height: 20px; background: {}; border-radius: 5px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile__user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = Profile.objects.all().select_related('user').order_by('user__username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== EXPERIENCE ADMIN ==========
class ExperienceAdminForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'profile' in self.fields:
            self.fields['profile'].queryset = Profile.objects.all().order_by('user__username')
            self.fields['profile'].label_from_instance = lambda obj: f"{obj.user.username} (ID: {obj.id})"

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    form = ExperienceAdminForm
    list_display = ('position', 'company', 'start_date', 'end_date', 'current', 'get_profile_display')
    list_filter = ('current', 'company', 'profile__user__username', 'start_date')
    search_fields = ('position', 'company', 'description', 'profile__user__username')
    date_hierarchy = 'start_date'
    
    # raw_id_fields ব্যবহার করবে না
    # raw_id_fields = ('profile',)  # এই লাইন থাকলে ডিলিট করো
    
    fieldsets = (
        ('Experience Details', {
            'fields': ('profile', 'company', 'position', 'start_date', 'end_date', 'current')
        }),
        ('Description', {
            'fields': ('description',),
        }),
    )
    
    def get_profile_display(self, obj):
        if obj.profile:
            return f"{obj.profile.user.username} (ID: {obj.profile.id})"
        return "No Profile"
    get_profile_display.short_description = 'Profile'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile__user')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "profile":
            kwargs["queryset"] = Profile.objects.all().select_related('user').order_by('user__username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# ========== ADMIN SITE CUSTOMIZATION ==========
# Unregister default User and register custom
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.site_header = "🔥 Portfolio Admin Dashboard 🔥"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Welcome - All User Profiles Available"

# Custom admin actions
def make_featured(modeladmin, request, queryset):
    queryset.update(featured=True)
make_featured.short_description = "Mark selected as featured"

def remove_featured(modeladmin, request, queryset):
    queryset.update(featured=False)
remove_featured.short_description = "Remove featured status"

# Add custom actions to Project admin
ProjectAdmin.actions = [make_featured, remove_featured]

# Add useful filters
from django.contrib.admin import SimpleListFilter

class HasImageFilter(SimpleListFilter):
    title = 'Has Profile Image'
    parameter_name = 'has_image'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Image'),
            ('no', 'No Image'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(profile_image_base64__isnull=False)
        if self.value() == 'no':
            return queryset.filter(profile_image_base64__isnull=True)
        return queryset

ProfileAdmin.list_filter = (HasImageFilter, 'user__is_staff', 'user__is_active')