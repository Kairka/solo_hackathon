from rest_framework import views, filters, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Category, Film, Like, Comment, Rating, Favorite
from .serializers import *
from .permissions import IsAdminUser, IsAuthor, IsAuthorOrIsAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return []
        return [IsAdminUser()]


class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return FilmsListSerializer
        elif self.action == 'retrieve':
            return FilmDetailSerializer
        return CreateFilmSerializer

    @action(['POST'], detail=True)
    def like(self, request, pk=None):
        film = self.get_object()
        user = request.user
        try:
            like = Like.objects.get(film=film, user=user)
            like.is_liked = not like.is_liked
            if like.is_liked:
                like.save()
            else:
                like.delete()
            message = 'like' if like.is_liked else 'dislike'
        except Like.DoesNotExist:
            Like.objects.create(film=film, user=user, is_liked=True)
            message = 'liked'
        return Response(message, status=200)

    @action(['POST'], detail=True)
    def favorite(self, request, pk=None):
        film = self.get_object()
        user = request.user
        try:
            favorite = Favorite.objects.get(film=film, user=user)
            favorite.is_favorite = not favorite.is_favorite
            if favorite.is_favorite:
                favorite.save()
            else:
                favorite.delete()
            message = 'added to favorites' if favorite.is_favorite else 'deleted in favorites'
        except Favorite.DoesNotExist:
            Favorite.objects.create(film=film, user=user, is_favorite=True)
            message = 'added to favorites'
        return Response(message, status=200)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return []
        elif self.action == 'create' or self.action == 'like' or self.action == 'favorite':
            return [IsAuthenticated()]
        return [IsAuthorOrIsAdmin()]


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'update':
            return [IsAuthor()]
        return [IsAuthorOrIsAdmin()]


class RatingViewSet(mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthor()]


class FavoritesListView(ListAPIView):
    permission_classes = [IsAuthor]
    serializer_class = FavoriteFilmsSerializer

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)
