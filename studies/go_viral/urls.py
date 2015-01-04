from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views

router = ExtendedSimpleRouter()

user_data_routes = router.register(r'user-data',
                                   views.UserDataViewSet,
                                   base_name='user-data')

user_data_routes.register(r'go-viral-ids',
                          views.GoViralIdViewSet,
                          base_name='user-data-go-viral-ids',
                          parents_query_lookups=['user_data'])

urlpatterns = router.urls
