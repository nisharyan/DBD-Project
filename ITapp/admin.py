from django.contrib import admin
from .models import Resource, SysAdmin, MagStaff, EquipDescr, Owns, Department


# Register your models here.

# @admin.register(Department)
# class Department(ImportExportModelAdmin):
#     list_display = ('deptName',)

admin.site.register(Resource)
admin.site.register(Owns)
admin.site.register(EquipDescr)
admin.site.register(Department)
admin.site.register(MagStaff)
admin.site.register(SysAdmin)