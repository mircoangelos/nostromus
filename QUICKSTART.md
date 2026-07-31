# 🚀 NOSTROMUS - Quick Start Guide

## 1️⃣ Clonar & Setup

```bash
cd xss-example
cp .env.example .env
# Editar .env con GEMINI_API_KEY
```

## 2️⃣ Iniciar Servicios (Docker)

```bash
docker-compose up -d

# Verificar que todo está corriendo
docker ps

# Ver logs
docker logs backend_nostromus -f
```

**Servicios disponibles:**
- PostgreSQL: `localhost:5432`
- Keycloak: `localhost:8080` (admin/admin)
- FastAPI: `localhost:8000` (OpenAPI en /docs)
- RabbitMQ: `localhost:15672` (guest/guest)

## 3️⃣ Configurar Keycloak

1. Ir a http://localhost:8080
2. Admin console: admin / admin
3. Crear Realm: `react-keycloak`
4. Crear Client: `FE-keycloak`
   - Redirect URI: `http://localhost:3000/*`
5. Crear Roles: `admin`, `sales`, `viewer`
6. Crear Users y asignar roles

## 4️⃣ Iniciar Frontend (React)

```bash
npm install
npm start

# Abrirá http://localhost:3000
# Haz login con usuario Keycloak
```

## 5️⃣ Iniciar Python Agent

```bash
cd agent

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar deps
pip install -r requirements.txt

# Iniciar consumer
python rabbitmq_consumer.py
```

## 6️⃣ Probar el Sistema

### Test 1: Crear evento de brute force
```bash
curl -X GET http://localhost:8000/api/incidents/test/brute-force
```

### Test 2: Crear evento de slow query
```bash
curl -X GET http://localhost:8000/api/incidents/test/slow-query
```

### Test 3: Ver RabbitMQ
```bash
# Ir a http://localhost:15672
# Ver queues: security_events, performance_events
# Ver consumers activos
```

### Test 4: Ver reportes generados
```bash
# Los reportes se guardan en: agent/reports/
# Ver los .txt generados
```

## 📊 URLs Importantes

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| React Frontend | http://localhost:3000 | Keycloak users |
| FastAPI Docs | http://localhost:8000/docs | (sin auth) |
| FastAPI Health | http://localhost:8000/health | (sin auth) |
| Keycloak | http://localhost:8080 | admin/admin |
| RabbitMQ Management | http://localhost:15672 | guest/guest |

## 🔄 Flujo Completo (End-to-End)

```
1. Acceder http://localhost:3000
2. Login con usuario de Keycloak
3. [OPCIONAL] POST /api/incidents → crear evento
   O acceder a http://localhost:8000/api/incidents/test/brute-force
4. FastAPI → publica a RabbitMQ
5. Agente Python → consume del queue
6. Gemini AI → analiza y genera reporte
7. Reporte guardado en agent/reports/
```

## 🧪 API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Crear Incidente
```bash
POST http://localhost:8000/api/incidents
Content-Type: application/json

{
  "event_type": "SECURITY_EVENT",
  "severity": "HIGH",
  "data": {
    "user_id": "test_user",
    "ip": "192.168.1.100",
    "attempts": 6
  },
  "description": "Brute force attack simulation"
}
```

### Test Endpoints
```bash
GET http://localhost:8000/api/incidents/test/brute-force
GET http://localhost:8000/api/incidents/test/slow-query
```

### Ver Reportes (TODO)
```bash
GET http://localhost:8000/api/reports
GET http://localhost:8000/api/reports/{report_id}
```

## 🐛 Troubleshooting

### Backend no inicia
```bash
# Ver logs
docker logs backend_nostromus

# Reiniciar
docker-compose restart backend
```

### Agent no consume eventos
```bash
# Verificar que RabbitMQ está corriendo
docker logs rabbitmq_nostromus

# Verificar que agent está escuchando
# Debe decir: "Waiting for events..."
```

### Keycloak no carga
```bash
# Puede tardar 1-2 minutos en iniciar
docker logs keycloak_nostromus

# Esperar y refrescar
```

### Gemini API error
```bash
# Verificar que .env tiene GEMINI_API_KEY
# La key debe ser válida y con permisos activados
```

## 📚 Documentación

- [README.md](./README.md) - Arquitectura completa
- [agent/agentSkills.md](./agent/agentSkills.md) - Reglas del agente
- [backend/models.py](./backend/models.py) - Data models
- [docker-compose.yml](./docker-compose.yml) - Servicios

## ✅ Checklist

- [ ] Docker instalado
- [ ] Python 3.11+ instalado
- [ ] Node.js 18+ instalado
- [ ] GEMINI_API_KEY en .env
- [ ] Keycloak configurado
- [ ] Services corriendo (docker ps)
- [ ] Frontend React iniciado
- [ ] Agent Python escuchando eventos
- [ ] Pruebas pasando (test endpoints)

---

**¿Necesitas ayuda?** Revisa los logs:
```bash
docker-compose logs -f
```
