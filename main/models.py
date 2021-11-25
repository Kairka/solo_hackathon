from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'


class Film(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='films')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='films')
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        summ = 0
        ratings = Rating.objects.filter(film=self)
        for rating in ratings:
            summ += rating.rate
        if len(ratings) > 0:
            return round(summ / len(ratings), 2)
        else:
            return 'No one rated'


class Comment(models.Model):
    film = models.ForeignKey(Film,
                             on_delete=models.CASCADE,
                             related_name='comments')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.film} --> {self.user}'


class Rating(models.Model):
    film = models.ForeignKey(Film,
                             on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=3,
                               decimal_places=2,
                               validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = (('user', 'film'), )
        index_together = (('user', 'film'), )


class Like(models.Model):
    film = models.ForeignKey(Film,
                             on_delete=models.CASCADE,
                             related_name='likes')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='likes')
    is_liked = models.BooleanField(default=False)


class Favorite(models.Model):
    film = models.ForeignKey(Film,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='favorites')
    is_favorite = models.BooleanField(default=False)
