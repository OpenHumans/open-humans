from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()

router.register(r'profile',
                views.ProfileViewSet,
                base_name='profile')

urlpatterns = router.urls
