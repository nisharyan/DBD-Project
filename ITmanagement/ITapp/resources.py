from import_export import resources
from .models import Department

class DepartmentResource(resources.ModelResource):
  class meta:
     model = Department