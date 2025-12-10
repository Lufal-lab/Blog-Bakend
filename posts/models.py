from django.db import models
from django.conf import settings
# settings.AUTH_USER_MODEL = "user.CustomUser"
# Esto permite que Django use tu modelo CustomUser en lugar del User por defecto.

# Create your models here.

class Post(models.Model):
    # =========================================================
    # PRIVACIDAD (LECTURA Y EDICIÓN)
    # =========================================================

    # Estas son las opciones válidas que aceptará el modelo.
    PRIVACY_PUBLIC = "public"
    PRIVACY_AUTH = "authenticated"
    PRIVACY_TEAM = "team"
    PRIVACY_AUTHOR = "author"

    PRIVACY_CHOICES = [
        (PRIVACY_PUBLIC, "Público"),
        (PRIVACY_AUTH, "Solo usuarios autenticados"),
        (PRIVACY_TEAM, "Solo usuarios del mismo equipo"),
        (PRIVACY_AUTHOR, "Solo el autor"),
    ]

    # El autor del post → un usuario
    # FK = ForeignKey = relación muchos-a-uno
    # Muchos posts pueden ser escritos por un mismo usuario
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # usar el CustomUser
        on_delete=models.CASCADE,   # si se borra el usuario, se borran sus posts
        related_name="posts"        # user.posts → todos los posts del usuario
    )
    
    # Título del post
    title = models.CharField(max_length=100)

    #Contenido del post
    content = models.TextField()

    #Se guarda automáticamente cuando el post se crea
    created_at = models.DateTimeField(auto_now_add=True)

    #Se actualiza automáticamente cada vez que el post se guarda
    updated_at = models.DateTimeField(auto_now=True)

    #PRIVACIDAD DE LECTURA Y EDICIÓN
    # Más adelante haremos enums o choices, por ahora solo textos
    privacy_read = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default=PRIVACY_PUBLIC
        )
    
    privacy_write = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default=PRIVACY_AUTHOR
        )
    

        # =========================================================
    # FUNCIONES DE PERMISOS (LECTURA Y EDICIÓN)
    # =========================================================

    def can_user_read(self, user):
        """
        Determina si un usuario puede LEER este post según la privacidad elegida.
        """

        # 1) PUBLICO → cualquiera puede leer, incluso no autenticados
        if self.privacy_read == self.PRIVACY_PUBLIC:
            return True

        # 2) SOLO USUARIOS AUTENTICADOS
        if self.privacy_read == self.PRIVACY_AUTH:
            return user.is_authenticated

        # 3) SOLO USUARIOS DEL MISMO TEAM
        if self.privacy_read == self.PRIVACY_TEAM:
            # usuario debe estar autenticado
            if not user.is_authenticated:
                return False

            # Si el autor NO tiene team, nadie puede leer por team
            if not hasattr(self.author, "team") or self.author.team is None:
                return False

            return user.team == self.author.team

        # 4) SOLO EL AUTOR
        if self.privacy_read == self.PRIVACY_AUTHOR:
            return user.is_authenticated and user == self.author

        # Por si acaso hubiera una opción inválida
        return False


    def can_user_edit(self, user):
        """
        Determina si un usuario puede EDITAR este post según la privacidad elegida.
        """

        # 1) PUBLICO → cualquier usuario puede editar (caso raro pero permitido)
        if self.privacy_write == self.PRIVACY_PUBLIC:
            return True

        # 2) SOLO USUARIOS AUTENTICADOS
        if self.privacy_write == self.PRIVACY_AUTH:
            return user.is_authenticated

        # 3) SOLO USUARIOS DEL MISMO TEAM
        if self.privacy_write == self.PRIVACY_TEAM:
            if not user.is_authenticated:
                return False

            if not hasattr(self.author, "team") or self.author.team is None:
                return False

            return user.team == self.author.team

        # 4) SOLO EL AUTOR
        if self.privacy_write == self.PRIVACY_AUTHOR:
            return user.is_authenticated and user == self.author

        # fallback
        return False
    
    # Cómo se mostrará el post en el admin / consola
    def __str__(self):
        return self.title

