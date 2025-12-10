# posts/serializers.py

from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """
    Este serializer convierte objetos Post <-> JSON.
    
    - Cuando el backend envía información → convierte Post a JSON.
    - Cuando el usuario envía datos (POST/PUT) → convierte JSON a Post.
        (serializer.is_valid() + serializer.save())
    
    ModelSerializer ya sabe cómo mapear los campos del modelo automáticamente.
    """

    class Meta:
        model = Post  # El modelo que se va a serializar

        # Campos que queremos mostrar y permitir escribir
        fields = [
            "id",
            "author",
            "title",
            "content",
            "created_at",
            "updated_at",
            "privacy_read",
            "privacy_write",
        ]

        # Estos campos NO deben ser modificables por el cliente
        read_only_fields = [
            "id",
            "author",        # el autor lo pondremos automáticamente en la vista
            "created_at",
            "updated_at",
        ]

    # ------------------------------------------------------------------
    # VALIDACIONES PERSONALIZADAS
    # ------------------------------------------------------------------

    def validate_title(self, value):
        """
        Ejemplo de validación:
        - Evitamos títulos vacíos o demasiado cortos.
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener mínimo 3 caracteres.")
        return value

    def validate(self, data):
        """
        Validación general del post:
        Aquí podrías agregar reglas más complejas.
        Por ejemplo:
        - No permitir ciertas combinaciones de privacidad
        - Asegurar que ciertos usuarios tengan permisos
        """

    # Validación cruzada entre campos (si necesitas reglas complejas)
    # Por ejemplo, podrías prohibir privacy_write == 'public' si no quieres que cualquiera edite.
        return data

    # ------------------------------------------------------------------
    # CREACIÓN Y ACTUALIZACIÓN DEL POST
    # ------------------------------------------------------------------

    def create(self, validated_data):
        """
        Cuando se crea un post desde un JSON:
        El método recibe 'validated_data', que contiene datos seguros,
        ya validados y listos para crear el Post.
        """
        # Cuando usamos serializer.save(author=usuario) en la view,
        # validated_data ya contiene lo seguro y listo para crear.
        return Post.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza un post existente.
        'instance' es el Post que ya existe.
        'validated_data' son los datos nuevos enviados desde el frontend.
        """
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
