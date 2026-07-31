"""
Servicio para gestionar usuarios sincronizados desde Keycloak
"""
from sqlalchemy.orm import Session
from models_db import User
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Servicio para sincronizar y obtener usuarios de Keycloak"""

    @staticmethod
    def get_or_create_user(db: Session, keycloak_user_info: dict) -> User:
        """
        Obtiene o crea un usuario basado en la información de Keycloak

        Args:
            db: Sesión de BD
            keycloak_user_info: Dict con info del usuario de Keycloak
                {
                    'sub': 'user_id',
                    'preferred_username': 'username',
                    'email': 'email@example.com',
                    'given_name': 'First',
                    'family_name': 'Last',
                    'realm_access': {'roles': ['admin', 'threat_analyst']}
                }

        Returns:
            Objeto User sincronizado con la BD
        """

        user_id = keycloak_user_info.get('sub')
        username = keycloak_user_info.get('preferred_username', user_id)
        email = keycloak_user_info.get('email', f'{username}@keycloak')
        full_name = f"{keycloak_user_info.get('given_name', '')} {keycloak_user_info.get('family_name', '')}".strip()

        # Obtener roles de Keycloak
        roles = keycloak_user_info.get('realm_access', {}).get('roles', [])
        primary_role = roles[0] if roles else 'viewer'

        # Buscar usuario existente
        user = db.query(User).filter(User.user_id == user_id).first()

        if user:
            # Actualizar información si cambió
            if user.email != email or user.role != primary_role:
                user.email = email
                user.role = primary_role
                if full_name:
                    user.full_name = full_name
                db.commit()
                logger.info(f"✓ Usuario actualizado: {username}")
        else:
            # Crear nuevo usuario
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name or username,
                role=primary_role,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"✓ Usuario creado desde Keycloak: {username}")

        return user

    @staticmethod
    def get_user_from_token(db: Session, token_data: dict) -> User:
        """
        Obtiene el usuario del diccionario del token JWT
        """
        return UserService.get_or_create_user(db, token_data)
