from django.urls import path
from . import views

urlpatterns = [
    path('', views.documento_list, name='documento_list'),
    path('documentos/', views.documento_list, name='documento_list'),
    path('documentos/crear/', views.documento_create, name='documento_create'),
    path('documentos/<int:pk>/', views.documento_detail, name='documento_detail'),
    path('documentos/<int:pk>/editar/', views.documento_edit, name='documento_edit'),
    path('documentos/<int:pk>/eliminar/', views.documento_delete, name='documento_delete'),
    path('documentos/<int:pk>/revision/', views.revision_create, name='revision_create'),
    path('clasificaciones/', views.clasificacion_list, name='clasificacion_list'),
    path('clasificaciones/crear/', views.clasificacion_create, name='clasificacion_create'),
    path('clasificaciones/<int:pk>/editar/', views.clasificacion_edit, name='clasificacion_edit'),
    path('historial/', views.historial_list, name='historial_list'),
]
