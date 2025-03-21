from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('simulador/', include('simulador.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('', RedirectView.as_view(url='/simulador/', permanent=False)),
]


# Para servir arquivos estáticos no modo dev
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

