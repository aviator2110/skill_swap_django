from django.contrib import admin
from .models import Category, Level, Format, Status, Offer, BookingRequest, Review, Favorite


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'level',
        'format',
        'status',
        'duration_minutes',
        'created_at',
    )
    list_filter = ('status', 'category', 'level', 'format', 'created_at')
    search_fields = ('title', 'description', 'author__username', 'author__email')
    list_editable = ('status',)
    ordering = ('-created_at',)
    actions = ['approve_offers', 'reject_offers', 'set_pending']

    @admin.action(description="Approve and Publish selected offers")
    def approve_offers(self, request, queryset):
        published_status = Status.objects.filter(slug='published').first()
        if published_status:
            updated = queryset.update(status=published_status)
            self.message_user(request, f"{updated} offer(s) published.")
        else:
            self.message_user(request, "Status 'Published' not found.", level='error')

    @admin.action(description="Reject selected offers")
    def reject_offers(self, request, queryset):
        rejected_status = Status.objects.filter(slug='rejected').first()
        if rejected_status:
            updated = queryset.update(status=rejected_status)
            self.message_user(request, f"{updated} offer(s) rejected.")
        else:
            self.message_user(request, "Status 'Rejected' not found.", level='error')

    @admin.action(description="Move selected offers to Pending moderation")
    def set_pending(self, request, queryset):
        pending_status = Status.objects.filter(slug='pending').first()
        if pending_status:
            updated = queryset.update(status=pending_status)
            self.message_user(request, f"{updated} offer(s) moved to Pending.")
        else:
            self.message_user(request, "Status 'Pending' not found.", level='error')


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'student', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('offer__title', 'student__username', 'message')
    list_editable = ('status',)
    ordering = ('-created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'offer', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('offer__title', 'author__username', 'comment')
    ordering = ('-created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'offer', 'created_at')
    search_fields = ('user__username', 'offer__title')
    ordering = ('-created_at',)

