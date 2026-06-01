from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginAPIView, RolViewSet, UsuarioViewSet,
    ClasificacionViewSet, DocumentoViewSet, HistorialViewSet
)

router = DefaultRouter()
router.register(r'roles', RolViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'clasificaciones', ClasificacionViewSet)
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'historial', HistorialViewSet)

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
