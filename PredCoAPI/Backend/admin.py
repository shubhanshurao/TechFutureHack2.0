from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register(Organization)
admin.site.register(Role)
admin.site.register(Profile)
admin.site.register(Division)
admin.site.register(UseCases)
# admin.site.register(Machine)
admin.site.register(Param)
admin.site.register(Device)
admin.site.register(Watcher)
# admin.site.register(Watchesddsdr)
admin.site.register(Alert)
admin.site.register(AnomalyAlert)
admin.site.register(Action)
admin.site.register(Job)

admin.site.register(AirflowJob)
admin.site.register(MLModel)
admin.site.register(Prediction)

admin.site.register(PatternDetector)
admin.site.register(DetectedPatternAlert)

admin.site.register(APIKey)
admin.site.register(ExtraKey)
