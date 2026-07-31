# 🤖 Nostromus - Claude AI Agent Guide

## Overview

El agente Claude analiza eventos de seguridad y performance usando **Claude 3.5 Sonnet** (modelo más reciente de Anthropic) y genera reportes detallados y accionables.

## ✨ Ventajas de Claude vs Gemini

| Aspecto | Claude | Gemini |
|--------|--------|--------|
| **Análisis de Seguridad** | ⭐⭐⭐⭐⭐ Experto | ⭐⭐⭐⭐ Bueno |
| **Generación de Reportes** | ⭐⭐⭐⭐⭐ Detallado | ⭐⭐⭐⭐ OK |
| **Razonamiento Complejo** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Bueno |
| **Velocidad** | ⭐⭐⭐⭐ Rápido | ⭐⭐⭐⭐⭐ Muy rápido |
| **Precisión** | ⭐⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ Alta |
| **Costo** | ✓ Competitivo | ✓ Competitivo |

---

## 🚀 Setup

### 1. Obtener Claude API Key

```bash
# Ve a: https://console.anthropic.com
# 1. Crea una cuenta
# 2. Ve a "API Keys"
# 3. Crea una nueva key
# 4. Cópiala
```

### 2. Configurar .env

```bash
# Opción A: Usar archivo .env.claude que creamos
cp .env.claude .env

# Opción B: Editar manualmente
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 3. Instalar Dependencias

```bash
cd agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
# Instala: anthropic, pika, python-dotenv
```

### 4. Iniciar Agente Claude

```bash
python claude_agent.py
```

---

## 🔄 Cómo Funciona

### Arquitectura

```
RabbitMQ (security_events)
    ↓
claude_agent.py (consumer)
    ↓
Event Received
    ├─ Format event data
    ├─ Load agent skills from agentSkills.md
    └─ Prepare system prompt
    ↓
Claude 3.5 Sonnet API Call #1
    ├─ Input: Event + Skills/Instructions
    ├─ Task: Analyze threat + provide recommendations
    └─ Output: Detailed analysis
    ↓
Claude 3.5 Sonnet API Call #2
    ├─ Input: Analysis from Call #1
    ├─ Task: Generate executive summary
    └─ Output: 1-2 sentence actionable recommendation
    ↓
Generate Report
    ├─ Report ID: REP_YYYYMMDD_HHMMSS
    ├─ Title: AI Security Analysis - EVENT_TYPE
    ├─ Content: Full analysis from Claude
    └─ Recommendation: Executive summary
    ↓
Publish to RabbitMQ (reports_queue)
    ↓
Report Worker consumes
    ├─ Save Report to PostgreSQL
    ├─ Update Incident status
    └─ Acknowledge message
    ↓
React Dashboard updates
    └─ User sees report
```

### Flujo Detallado de un Evento

```
EVENTO LLEGA: SECURITY_EVENT - Login fallido (5 intentos)
│
├─ Paso 1: Parse JSON del evento
│  {
│    "event_type": "SECURITY_EVENT",
│    "severity": "HIGH",
│    "user_id": "malicious_user",
│    "data": {
│      "ip": "192.168.1.100",
│      "attempts": 5
│    }
│  }
│
├─ Paso 2: Format para Claude
│  "Event Type: SECURITY_EVENT
│   Severity: HIGH
│   User ID: malicious_user
│   IP: 192.168.1.100
│   Attempts: 5"
│
├─ Paso 3: Load System Instructions (agentSkills.md)
│  "You are a Security Analyst...
│   If login attempts > 5, lock the user..."
│
├─ Paso 4: Call Claude #1 - Analyze
│  ┌─ System: Skills
│  ├─ User: Event description
│  └─ Claude Response:
│    "THREAT ASSESSMENT: HIGH RISK
│     This appears to be a brute force attack
│     
│     ROOT CAUSE: Attacker attempting unauthorized access
│     
│     IMMEDIATE ACTIONS:
│     1. Lock user account immediately
│     2. Alert security team
│     3. Review access logs from this IP
│     
│     PREVENTION:
│     1. Implement CAPTCHA after 3 failed attempts
│     2. Add IP-based rate limiting
│     3. Enable MFA for all users
│     
│     IMPACT: Potential unauthorized access"
│
├─ Paso 5: Call Claude #2 - Executive Summary
│  ┌─ Input: Analysis from Paso 4
│  └─ Claude Response:
│    "Lock user account immediately and review 
│     access logs from 192.168.1.100 for 
│     unauthorized access attempts in the last 24h."
│
├─ Paso 6: Generate Report
│  {
│    "report_id": "REP_20260730_143022",
│    "severity": "HIGH",
│    "title": "AI Security Analysis - SECURITY_EVENT",
│    "content": "[Full analysis from Paso 4]",
│    "recommendation": "[Executive summary from Paso 5]",
│    "ai_model": "Claude 3.5 Sonnet",
│    "generated_at": "2026-07-30T14:30:22"
│  }
│
└─ Paso 7: Publish a reports_queue → Persist en BD
```

---

## 📊 Ejemplos de Reportes Generados

### Ejemplo 1: Brute Force Attack

```
═══════════════════════════════════════════════════════
[CLAUDE AGENT] - SECURITY_EVENT
═══════════════════════════════════════════════════════

THREAT ASSESSMENT
═════════════════
Severity: HIGH - This represents a clear and immediate threat

The pattern of 6 failed login attempts from a single IP address 
in rapid succession is consistent with brute force attack methodology.

ROOT CAUSE ANALYSIS
═══════════════════
The attacker is attempting to gain unauthorized access through 
credential guessing. The high failure count suggests either:
1. Automated password spraying tool
2. Dictionary attack
3. Compromised credentials being tested

IMMEDIATE ACTIONS RECOMMENDED
══════════════════════════════
1. BLOCK: Lock the target account immediately
2. INVESTIGATE: Review all authentication logs from 192.168.1.100
3. ALERT: Notify security team of ongoing attack
4. ISOLATE: Consider temporary IP blocking if attack continues

LONG-TERM PREVENTION MEASURES
══════════════════════════════
1. Implement progressive delays after failed attempts
2. Add CAPTCHA after 3 failed attempts
3. Enable multi-factor authentication (MFA) for all users
4. Deploy rate limiting on login endpoints
5. Use geo-IP blocking for suspicious locations
6. Implement login attempt alerting system

IMPACT ASSESSMENT
═════════════════
- Potential: Account compromise
- Risk Level: HIGH - Attacker has clearly targeted this account
- Recommended Response: Immediate account lockdown
- Escalation: Alert user of compromise attempt

═══════════════════════════════════════════════════════
```

### Ejemplo 2: Slow Query Performance

```
═══════════════════════════════════════════════════════
[CLAUDE AGENT] - PERFORMANCE_EVENT
═══════════════════════════════════════════════════════

THREAT ASSESSMENT
═════════════════
Severity: MEDIUM

A GraphQL query execution time exceeding 2000ms indicates 
potential performance degradation that may impact user experience.

ROOT CAUSE ANALYSIS
═══════════════════
Possible causes:
1. Missing database indexes on frequently queried columns
2. N+1 query problem in GraphQL resolvers
3. Large dataset filtering without pagination
4. Unoptimized JOIN operations
5. Database lock contention

IMMEDIATE ACTIONS RECOMMENDED
══════════════════════════════
1. PROFILE: Run database query analyzer on the slow query
2. OPTIMIZE: Check for missing indexes on WHERE/JOIN columns
3. CACHE: Implement caching for frequently accessed data
4. PAGINATE: Add pagination to large result sets
5. MONITOR: Track query performance over next hour

LONG-TERM PREVENTION MEASURES
══════════════════════════════
1. Implement database query monitoring and alerts
2. Set up automated index recommendations
3. Add query complexity analysis to CI/CD pipeline
4. Use APM tools (Application Performance Monitoring)
5. Train developers on query optimization best practices
6. Implement query execution time budgets

IMPACT ASSESSMENT
═════════════════
- Current Impact: Degraded user experience for affected queries
- Risk Level: MEDIUM - Affects availability
- Performance: 2000ms is at threshold, aim for < 500ms
- Scale: Impacts system scalability

═══════════════════════════════════════════════════════
```

---

## 🎯 Model Configuration

El agente usa **Claude 3.5 Sonnet**:

```python
client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1500,  # Análisis detallado
    system=skills,    # Instrucciones del agente
    messages=[...]
)
```

**Por qué Sonnet?**
- ⭐ Mejor relación precio/rendimiento
- ⭐ Excelente para análisis de seguridad
- ⭐ Token limit: 200K (suficiente para reportes)
- ⭐ Velocidad: ~1-2 segundos por análisis

---

## 🔧 Customización

### Modificar Agent Skills

Edita `agent/agentSkills.md` para cambiar comportamiento:

```markdown
### 1. Brute Force Attack Detection
- **Trigger**: Login attempts > 5 in 5 minutes
- **Action**: Lock user account temporarily
- **Severity**: HIGH
- **Response**: Generate security report + notify admin
```

### Cambiar Prompts

En `claude_agent.py`:

```python
def format_event_for_analysis(event_data):
    """Personaliza aquí el formato del evento"""
    return f"""
Custom Analysis Request
=======================
Event: {event_data}
Please provide: [tus instrucciones personalizadas]
"""
```

### Agregar Nuevos Tipos de Análisis

```python
def analyze_event_with_claude(event_data):
    # Agregar lógica adicional según event_type
    if event_type == "COMPLIANCE_EVENT":
        # Análisis específico de cumplimiento
        pass
```

---

## 📈 Monitoreo

### Ver Logs del Agente

```bash
tail -f agent/nostromus_claude.log
```

### Métricas

Los reportes almacenan:
- `ai_model`: "Claude 3.5 Sonnet"
- `ai_response_time`: Milliseconds del análisis
- `generated_at`: Timestamp ISO 8601

---

## 🐛 Troubleshooting

### Error: "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
# Verifica que esté en .env
```

### Error: "401 Unauthorized"
```bash
# Key inválida o expirada
# Ve a https://console.anthropic.com y genera una nueva
```

### Agent no procesa eventos
```bash
# 1. Verifica RabbitMQ
docker logs rabbitmq_nostromus

# 2. Verifica Agent logs
tail -f agent/nostromus_claude.log

# 3. Reinicia Agent
python claude_agent.py
```

### Reportes vacíos
```bash
# Claude tardó demasiado, aumenta max_tokens:
# En claude_agent.py:
max_tokens=2000  # Aumenta si necesitas análisis más largo
```

---

## 📚 API Reference

### Crear Evento para Análisis

```python
event = {
    "event_type": "SECURITY_EVENT",  # SECURITY, PERFORMANCE, OPERATIONAL
    "severity": "HIGH",               # LOW, MEDIUM, HIGH, CRITICAL
    "user_id": "username",
    "data": {
        "ip": "192.168.1.100",
        "attempts": 5,
        "resource": "login_endpoint",
        "custom_field": "value"
    },
    "description": "5 failed login attempts from single IP"
}
```

### Reporte Generado

```json
{
    "report_id": "REP_20260730_143022",
    "severity": "HIGH",
    "title": "AI Security Analysis - SECURITY_EVENT",
    "content": "Análisis detallado completo...",
    "analysis": "Igual que content",
    "recommendation": "Resumen ejecutivo de 1-2 líneas",
    "ai_model": "Claude 3.5 Sonnet",
    "generated_at": "2026-07-30T14:30:22.123456"
}
```

---

## 🎓 Mejores Prácticas

1. **Mantener agentSkills.md actualizado** - Refleja amenazas actuales
2. **Monitorear token usage** - Claude cobra por tokens, optimiza prompts
3. **Usar system instructions efectivas** - Input de calidad = output de calidad
4. **Versionar reportes** - Guarda histórico para análisis de tendencias
5. **Iterar en prompts** - Prueba diferentes instrucciones, mejora resultados

---

## 📞 Soporte

- Documentación Claude: https://docs.anthropic.com
- API Reference: https://docs.anthropic.com/en/api/messages
- Status Page: https://status.anthropic.com

---

**Nostromus v0.1.0 - Claude AI Agent Edition** ✅
