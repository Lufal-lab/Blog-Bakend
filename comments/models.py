from django.db import models
from django.conf import settings
from posts.models import Post
from django.core.exceptions import ValidationError
# Create your models here.


class Comment(models.Model):

    #El usuario que escribió el comentario
    #Muchos comentarios pueden ser escritos por el mismo usuario
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # usar el CustomUser
        on_delete=models.CASCADE,   # si se borra el usuario, se borran sus comentarios
        related_name="comments"        # user.comments → comentarios de un usuario
    )

    #El post al que pertenece este comentario
    #Muchos comentarios pueden ser del mismo post
    post = models.ForeignKey(
        Post,                       #usar el post creado
        on_delete=models.CASCADE,   #si se borra el post los comentarios se deben borrar
        related_name="comments")    #post.comments → comentarios de un post

    #Texto del comentario
    content = models.TextField(blank=False, null=False)

    #Fecha de creación del comentario
    created_at = models.DateTimeField(auto_now_add=True)

    # -----------------------------------------------------
    # VALIDACIÓN MANUAL DEL MODELO
    # Esto SÍ evita guardar contenido vacío.
    # -----------------------------------------------------
    def clean(self):
        # Si está vacío o solo espacios → error
        if not self.content or self.content.strip() == "":
            raise ValidationError("El contenido del comentario no puede estar vacío.")
        
    # -----------------------------------------------------
    # Sobrescribimos save() para llamar a clean() antes de guardar
    # -----------------------------------------------------
    def save(self, *args, **kwargs):
        self.clean()  # ejecuta la validación manual
        super().save(*args, **kwargs)

    def __str__(self):
        # no devolveremos demasiado contenido para evitar prints enormes
        return self.content
