from rest_framework import serializers

from main.models import Category, Film, Comment, Rating, Favorite


class FilmsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ('name', 'image',  'average_rating')


class FilmDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ('name', 'description', 'image', 'category', 'average_rating')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['like'] = instance.likes.count()
        rep['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        return rep


class CategoryDetailSerializer(serializers.ModelSerializer):
    films = FilmsListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'title', 'films')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CreateFilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        exclude = ('user', )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        if request.user.is_anonymous:
            raise serializers.ValidationError('Can create only authorized user')
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    film = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Film.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'film', 'text', 'user', )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    film = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Film.objects.all())
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'rate', 'film', 'user', )

    def validate(self, attrs):
        film = attrs.get('film')
        request = self.context.get('request')
        user = request.user
        if Film.objects.filter(film=film, user=user).exists():
            raise serializers.ValidationError('Impossible to rate twice')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)


class FavoriteFilmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('film', 'id')

        def get_favorite(self, obj):
            if obj.favorite:
                return obj.favorite
            return ''

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep['favorite'] = self.get_favorite(instance)
            return rep
