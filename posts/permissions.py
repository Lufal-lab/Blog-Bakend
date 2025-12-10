from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser

class ObjectPermissionHelpers:
    """  
    Pequeños helpers para centrailizar las reglas que ta estan definidas en los modelos 
    """

    @staticmethod
    def user_is_authenticated(request_user):
        """  
        Decuelve True si el request_user está autenticado.
        No se intenta setear is_authenticated, solo leerlo.
        """
        return getattr(request_user, "is_authenticated", False)
    
    @staticmethod
    def same_team(request_user, author):
        """  
        True si ambos usuarios están en el mismo team (y estan autenticados).
        """
        if not ObjectPermissionHelpers.user_is_authenticated(request_user):
            return False
        #Si el author o el request_user no tienen team -> False
        return getattr(request_user, "team", None) is not None and getattr(author, "team", None) == request_user.team
    
#-------------------------------------------------------
#PERMISO DE LECTURA
#-------------------------------------------------------
class CanReadPost(BasePermission):
    """  
    Permiso a nivel objeto para decidir si 'request.user' puede LEER 'obj' (POST).
    Usar has_object_permission que recibe (request, view, obj).
    """

    def has_object_permission(self, request, view, obj):
        """  
        Decide si alguien puede LEER el post
        """

        #Si es públic cualquiera puede LEER el post
        if obj.privacy_read == obj.PRIVACY_PUBLIC:
            return True
        
        #Si es solo usuarios logeados request.user.is_authenticated debe ser True
        if obj.privacy_read == obj.PRIVACY_AUTH:
            return ObjectPermissionHelpers.user_is_authenticated(request.user)
        
        # Si es solo team. Ambos deben pertenecer al mismo team
        if obj.privacy_read == obj.PRIVACY_TEAM:
            return ObjectPermissionHelpers.same_team(request.user, obj.author)

        # Si es solo el autor
        if obj.privacy_read == obj.PRIVACY_AUTHOR:
            return request.user == obj.author
        
        #fallback (retroceder)
        return False
    
    
# =====================================================
# PERMISO DE EDICIÓN
# =====================================================
class CanEditPost(BasePermission):
    """
    Permiso a nivel objeto para decidir si se puede EDITAR/ELIMINAR el post.
    """


    def has_object_permission(self, request, view, obj):
        # si se fuera a usar has_permission (nivel vista) lo pondríamos aquí.
        # Pero para comprobar el objeto necesitamos has_object_permission.

        # 1) Public -> cualquiera puede editar (raro, pero lo permitimos si el autor lo marca)
        if obj.privacy_write == obj.PRIVACY_PUBLIC:
            return True

        # 2) Authenticated -> cualquier usuario autenticado
        if obj.privacy_write == obj.PRIVACY_AUTH:
            return ObjectPermissionHelpers.user_is_authenticated(request.user)

        # 3) Team -> usuarios del mismo equipo solamente
        if obj.privacy_write == obj.PRIVACY_TEAM:
            return ObjectPermissionHelpers.same_team(request.user, obj.author)

        # 4) Author -> solo el autor puede editar/eliminar
        if obj.privacy_write == obj.PRIVACY_AUTHOR:
            return request.user == obj.author

        return False