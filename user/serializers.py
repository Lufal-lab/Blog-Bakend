from rest_framework import serializers
from .models import CustomUser, Team

class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo CustomUser.
    Se usa principalmente para:
    - Crear nuevos usuarios
    - Devolver información del usuario a la API
    """

    # Campo password solo se escribe, nunca se devuelve en la respuesta JSON
    password = serializers.CharField(
        write_only=True, # Esto evita que se envíe la contraseña al frontend
        required=True, # Obligatorio para crear usuario
        min_length=8) # Se requiere mínimo 8 caracteres

    class Meta:
        """
        Configuración interna del serializer
        """
        model = CustomUser #Modelo a serializar

        fields = ['id', 'email', 'password', 'team'] #Campos a aceptar/Se devolverá el serializer

        read_only_fields = ['id'] #id generado automáticamente, no se puede escribir

        # ------------------------------------------------------------------
        # MÉTODO CREATE: SE EJECUTA CUANDO LLAMAMOS serializer.save()
        # ------------------------------------------------------------------
        def create(self, validated_data):
            """
            Crea un usuario nuevo con contraseña encriptada
            validated_data: diccionario con datos validados desde la request (JSON)
            """
            # Se wxtrae la contraseña del diccionario para procesarla aparte
            password = validated_data.pop('password')
            # Se crea una instancia de usuario con los otros campos (email y team)
            user = CustomUser(**validated_data)
            #Encriptado de la contraseña
            user.set_password(password)
            #Guardar usuario en la base de datos
            user.save()
            #Retornar usuario creado
            return user