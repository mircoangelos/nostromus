#!/usr/bin/env python3
"""
Script para importar realm, roles y usuarios a Keycloak via API REST
"""

import json
import requests
import time

KEYCLOAK_URL = "http://localhost:8080"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"
REALM_NAME = "nostromus"

def get_admin_token():
    """Obtiene token de admin para APIs"""
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": ADMIN_USER,
        "password": ADMIN_PASSWORD,
    }
    response = requests.post(url, data=data)
    return response.json()["access_token"]

def create_realm(token):
    """Crea el realm nostromus"""
    url = f"{KEYCLOAK_URL}/admin/realms"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    realm_data = {
        "realm": REALM_NAME,
        "enabled": True,
        "displayName": "Nostromus - Incident Response System",
    }

    response = requests.post(url, json=realm_data, headers=headers)
    if response.status_code in [201, 409]:  # 409 = ya existe
        print(f"✓ Realm '{REALM_NAME}' creado o ya existe")
        return True
    else:
        print(f"✗ Error creando realm: {response.status_code} - {response.text}")
        return False

def create_roles(token):
    """Crea los roles"""
    roles = [
        {"name": "admin", "description": "Full access to Nostromus system"},
        {"name": "threat_analyst", "description": "Can analyze incidents and generate reports"},
        {"name": "operator", "description": "Can manage operational tasks"},
        {"name": "viewer", "description": "Can view incidents and reports only"},
    ]

    for role in roles:
        url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.post(url, json=role, headers=headers)
        if response.status_code in [201, 409]:
            print(f"✓ Rol '{role['name']}' creado o ya existe")
        else:
            print(f"✗ Error creando rol '{role['name']}': {response.status_code}")

def create_client(token):
    """Crea el cliente nostromus-client"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/clients"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    client_data = {
        "clientId": "nostromus-client",
        "name": "Nostromus Client",
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "publicClient": False,
        "secret": "nostromus-secret-key",
        "redirectUris": ["http://localhost:3000/*"],
        "webOrigins": ["http://localhost:3000"],
        "protocol": "openid-connect",
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "directAccessGrantsEnabled": True,
    }

    response = requests.post(url, json=client_data, headers=headers)
    if response.status_code in [201, 409]:
        print(f"✓ Cliente 'nostromus-client' creado o ya existe")
        return True
    else:
        print(f"✗ Error creando cliente: {response.status_code} - {response.text}")
        return False

def create_users(token):
    """Crea los usuarios desde realm-export.json"""
    with open("realm-export.json", "r") as f:
        realm_data = json.load(f)

    users = realm_data.get("users", [])

    for user in users:
        url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        user_data = {
            "username": user["username"],
            "email": user["email"],
            "emailVerified": True,
            "enabled": True,
            "firstName": user.get("firstName", ""),
            "lastName": user.get("lastName", ""),
            "credentials": [
                {
                    "type": "password",
                    "value": user["credentials"][0]["value"],
                    "temporary": False,
                }
            ],
        }

        response = requests.post(url, json=user_data, headers=headers)
        if response.status_code in [201, 409]:
            user_id = response.json().get("id") if response.status_code == 201 else get_user_id(token, user["username"])
            print(f"✓ Usuario '{user['username']}' creado o ya existe")

            # Asignar roles
            assign_roles(token, user_id, user.get("realmRoles", []))
        else:
            print(f"✗ Error creando usuario '{user['username']}': {response.status_code}")

def get_user_id(token, username):
    """Obtiene el ID de un usuario por nombre"""
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users?username={username}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        return response.json()[0]["id"]
    return None

def assign_roles(token, user_id, role_names):
    """Asigna roles a un usuario"""
    if not role_names:
        return

    # Obtener IDs de roles
    role_ids = []
    for role_name in role_names:
        url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/roles/{role_name}"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            role_ids.append(response.json())

    if not role_ids:
        return

    # Asignar roles
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}/role-mappings/realm"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(url, json=role_ids, headers=headers)
    if response.status_code == 204:
        print(f"  → Roles asignados: {', '.join(role_names)}")
    else:
        print(f"  ✗ Error asignando roles: {response.status_code}")

def main():
    print("🚀 Iniciando importación de realm Nostromus...")
    print()

    # Esperar a que Keycloak esté listo
    print("⏳ Esperando a Keycloak...")
    for i in range(30):
        try:
            requests.get(f"{KEYCLOAK_URL}/health/ready")
            print("✓ Keycloak está listo")
            break
        except:
            time.sleep(1)

    print()
    print("🔑 Obteniendo token de admin...")
    token = get_admin_token()
    print("✓ Token obtenido")
    print()

    print("📋 Creando realm...")
    create_realm(token)
    print()

    print("🔐 Creando roles...")
    create_roles(token)
    print()

    print("👤 Creando cliente...")
    create_client(token)
    print()

    print("👥 Creando usuarios...")
    create_users(token)
    print()

    print("✅ ¡Importación completada!")
    print()
    print("Usuarios disponibles:")
    print("  - miguel (admin) / miguel")
    print("  - ariel (threat_analyst) / ariel")
    print("  - jhonny (threat_analyst) / jhonny")
    print("  - rodney (threat_analyst) / rodney")
    print("  - gramsci (threat_analyst) / gramsci")
    print("  - xavier (threat_analyst) / xavier")
    print("  - diego (operator) / diego")
    print("  - sofia (viewer) / sofia")

if __name__ == "__main__":
    main()
