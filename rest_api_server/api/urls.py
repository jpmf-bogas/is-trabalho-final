from django.urls import path
from .views.file_views import FileUploadView
# from .views.xml_validation_views import XMLValidationView
from .views.csv_to_xml_views import CSVToXMLView
from .views.users import GetAllUsers

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    # path('validate-xml/', XMLValidationView.as_view(), name='validate-xml'),
    path('convert-csv-to-xml/', CSVToXMLView.as_view(), name='convert-csv-to-xml'),
    path('users/', GetAllUsers.as_view(), name='users'),
]