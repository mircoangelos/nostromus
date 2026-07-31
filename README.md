# 🛡️ Nostromus - Incident Response & AI Security Monitor

Sistema **100% Python event-driven** de **detección y respuesta a incidentes** con capacidades de IA integrada. Monitorea eventos de seguridad y performance, analiza contexto con Google Gemini, y ejecuta acciones automáticas.

## 📊 Arquitectura Completa

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│           (Keycloak Auth + Incident Reports)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Backend (Python 3.11)                   │
│  - /api/incidents    (Create incidents)                      │
│  - /api/reports      (View reports & analytics)              │
│  - Keycloak Integration + CORS                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ AMQP
┌──────────────────────▼──────────────────────────────────────┐
│              RabbitMQ Event Bus (Queue Routing)              │
│  - security_events ──→ AI Agent                              │
│  - performance_events ──→ AI Agent                           │
│  - operational_events ──→ Workers                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌──────────┐
   │ AI Agent│   │ Workers │   │ Analytics│
   │ (Gemini)│   │(Actions)│   │ (Future) │
   └────┬────┘   └────┬────┘   └──────────┘
        │             │
        └──────────┬──────────┘
                   │ SQL
        ┌──────────▼──────────┐
        │   PostgreSQL DB     │
        │ - Incidents         │
        │ - Reports           │
        │ - Audit Trail       │
        └─────────────────────┘
```

## 🚀 Stack Tecnológico

### Frontend (React 18 + TypeScript)
- Dashboard de reportes en tiempo real
- Panel de administración
- Autenticación SSO con Keycloak
- Control de roles (admin, sales, viewer)
- DOMPurify para XSS prevention

### Backend (FastAPI + Python 3.11) ⭐ TODO PYTHON
- REST API con OpenAPI/Swagger
- Autenticación Keycloak
- Integración con RabbitMQ (Producer)
- Rutas protegidas por roles
- Async/await para máximo rendimiento

### AI Agent (Google Gemini + Python)
- Procesamiento de eventos de seguridad
- Análisis automático de performance
- Generación de reportes automáticos
- Ejecución de acciones (lock account, alert, etc.)
- Consumidor RabbitMQ con AFC (Automatic Function Calling)

### Message Queue (RabbitMQ)
- Event Bus descentralizado
- 3 queues: security_events, performance_events, operational_events
- Persistent delivery
- Dead letter queues (próximamente)

### Base de Datos (PostgreSQL 15)
- Incidentes y eventos
- Reportes generados
- Audit trail completo
- Sesiones de Keycloak

### Autenticación (Keycloak)
- OIDC/OAuth2
- RBAC (Role-Based Access Control)
- Multi-tenancy (futuro)
- SSO integration

## 📋 Requisitos

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose
- Google Gemini API Key

## ⚙️ Setup Local (TODO PYTHON 🐍)

### Requisitos Previos
- Python 3.11+
- Node.js 18+ (solo para React Frontend)
- Docker & Docker Compose
- Google Gemini API Key

### 1. Clonar y configurar variables
```bash
git clone <repo>
cd xss-example
cp .env.example .env
# Editar .env con tus valores
```

### 2. Iniciar infraestructura (Docker)
```bash
docker-compose up -d
# Esperará a que todos los servicios estén listos
# PostgreSQL (5432) ✓
# Keycloak (8080) ✓
# RabbitMQ (5672) ✓
# FastAPI Backend (8000) ✓
```

### 3. Configurar Keycloak (http://localhost:8080)
- **Admin**: `admin / admin`
- Crear **Realm**: `react-keycloak`
- Crear **Client**: `FE-keycloak` (con CORS a http://localhost:3000)
- Crear **Roles**: `admin`, `sales`, `viewer`
- Crear **Users** con roles asignados

### 4. Iniciar Frontend (React)
```bash
npm install
npm start
# Abrirá http://localhost:3000
# Login: usa usuario de Keycloak
```

### 5. FastAPI Backend (ya corre en Docker)
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **Health**: http://localhost:8000/health
- **Crear evento de prueba**: POST http://localhost:8000/api/incidents

### 6. Iniciar Python Agent (RabbitMQ Consumer)
```bash
cd agent

# Crear virtual environment
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar consumer
python rabbitmq_consumer.py
# Esperará eventos en: security_events, performance_events, operational_events
```

### 7. Ver RabbitMQ Management
- **URL**: http://localhost:15672
- **User**: guest / guest
- Ver queues, mensajes, y consumers activos

## 📁 Estructura de Carpetas

```
xss-example/
├── src/                          # React Frontend
│   ├── auth/                     # Keycloak integration
│   ├── features/                 # Pages (sales, admin, home)
│   ├── hooks/                    # Custom hooks
│   ├── reducers/                 # State management
│   └── mocks/                    # Mock handlers
├── api/                          # Express Backend
│   ├── index.js                  # Server entry
│   └── routes/                   # API endpoints
├── agent/                        # Python AI Agent
│   ├── firstbornAgent.py         # Main agent
│   ├── generatorFirstVersion.py  # Action handlers
│   ├── agentSkills.md            # Agent instructions
│   ├── event*.json               # Demo events
│   └── requirements.txt          # Python deps
├── docker-compose.yml            # Services config
├── package.json                  # Node deps
└── .env.example                  # Environment template
```

## 🔄 Flujo de Eventos (Actual - Fase 1)

1. **Event Ingestion**: Agent lee eventos JSON locales
2. **Reasoning**: Gemini analiza el evento
3. **Actions**: Agent ejecuta tools automáticas
4. **Reporting**: Genera reportes en disco

## 🔄 Flujo Esperado (Fase 2 - RabbitMQ)

1. App emite evento → Incident Service
2. Incident Service → RabbitMQ
3. RabbitMQ → AI Agent Service
4. Agent → Action Worker
5. Worker → Database

## 📊 Casos de Uso

### Seguridad
- 🔴 **Brute Force**: Login fallidos (5+) → Bloquear cuenta
- 🟠 **Anomalía**: Acceso desde IP desconocida → Alert
- 🟡 **Session**: Expiración de sesión → Re-auth

### Performance
- ⚡ **Query Lenta**: Detectar queries > 2s → Optimizar índices
- 💾 **Memory Leak**: Alta memoria → Alert a SRE
- 📡 **Latencia**: API > 500ms → Escalar

## 🔐 Seguridad Implementada

- ✅ Autenticación con Keycloak + JWT
- ✅ Autorización basada en roles (RBAC)
- ✅ DOMPurify para prevenir XSS
- ✅ CORS configurado
- ⏳ Rate limiting (próximamente)
- ⏳ Audit logs (próximamente)

## 🧪 Testing

```bash
# Frontend tests
npm test

# Backend tests (cuando estén implementados)
cd api && npm test

# Agent tests (cuando estén implementados)
cd agent && python -m pytest
```

## 📈 Roadmap

- [ ] Implementar RabbitMQ
- [ ] Crear Incident Service (Python/Node)
- [ ] Implementar Report Worker
- [ ] Dashboard de reportes en tiempo real
- [ ] Audit trail completo
- [ ] WebSocket para actualizaciones en vivo
- [ ] Métricas con Prometheus
- [ ] Alertas con Slack/Teams

## 🤝 Contribuir

```bash
git checkout -b feature/tu-feature
git commit -am "Descripción clara"
git push origin feature/tu-feature
```

## 📞 Soporte

- 📧 miguel.villanueva@sciencelogic.com
- 📚 Documentación: (próximamente)
- 🐛 Issues: GitHub Issues

---

**Nostromus v0.1.0** | Seguridad y IA al servicio de tus aplicaciones 🚀
