from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()

# TODO: Change to 'profile' to 'member' here and in API implementations?
router.register(r'profile',
                views.MemberViewSet,
                base_name='profile')

urlpatterns = router.urls
