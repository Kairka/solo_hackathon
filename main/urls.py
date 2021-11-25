from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register('films', FilmViewSet, 'films')
router.register('categories', CategoryViewSet, 'subjects')
router.register('comments', CommentViewSet, 'comments')
router.register('ratings', RatingViewSet, 'ratings')

urlpatterns = [
    path('', include(router.urls)),
    path('favourites_list/', FavoritesListView.as_view())
]
