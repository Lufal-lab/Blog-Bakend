from django.db import models
from django.conf import settings
from posts.models import Post

# Create your models here.
class Like(models.Model):

    #Usuario que dio like
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # usar el CustomUser
        on_delete=models.CASCADE,   # si se borra el usuario, se borran sus likes
        related_name= "likes"       # user.likes → likes de un usuario
    )

    #Post al que se le dio like
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )

    #Fecha del like
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Esto evita que un usuario pueda dar más de un like al mismo post
        # Es una regla a nivel de base de datos
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.email} dio like a {self.post.title}"