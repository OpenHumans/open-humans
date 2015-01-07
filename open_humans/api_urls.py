from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()

router.register(r'member',
                views.MemberViewSet,
                base_name='member')

urlpatterns = router.urls
