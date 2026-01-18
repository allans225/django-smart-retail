from django.contrib import admin
from .models import Profile, Address

class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

    fields = (
        'street', 'number', 'neighborhood', 
        'supplement', 'city', 'state', 'zip_code'
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'get_birth_date', 'cpf')
    list_display_links = ('pk', 'user')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'cpf')
    inlines = [AddressInline]
    ordering = ('-pk',)

    # exibir a data de nascimento formatada 
    def get_birth_date(self, obj):
        return obj.birth_date
    get_birth_date.short_description = 'Nascimento'

admin.site.register(Profile, ProfileAdmin)
