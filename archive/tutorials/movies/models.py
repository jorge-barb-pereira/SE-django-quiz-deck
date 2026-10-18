from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    
    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"

class Movie(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    
    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"

    def __str__(self):
        return f'({self.title})({self.year})'

# Create your models here.
