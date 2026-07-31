# 🤖 Claude vs Gemini - Agentes de IA para Nostromus

## 📊 Comparación Rápida

| Aspecto | Claude 3.5 Sonnet | Gemini 2.0 Flash |
|---------|------------------|-----------------|
| **Análisis de Seguridad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Reportes** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Velocidad** | ⭐⭐⭐⭐ (~2-3s) | ⭐⭐⭐⭐⭐ (~1-2s) |
| **Costo** | $3/$15 per 1M tokens | $0.075/$0.30 per 1M tokens |
| **Profundidad Análisis** | ⭐⭐⭐⭐⭐ Experto | ⭐⭐⭐⭐ Bueno |
| **Razonamiento** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Muy bueno |
| **Recomendación** | ✅ RECOMENDADO | Alternativa válida |

---

## 🎯 Cuándo usar cada uno

### Usa CLAUDE si...
- ✅ Necesitas reportes profesionales y detallados
- ✅ Importa la calidad del análisis sobre la velocidad
- ✅ Quieres explicaciones profundas
- ✅ Necesitas recomendaciones estratégicas
- ✅ Presupuesto permite (es más caro)

### Usa GEMINI si...
- ✅ Necesitas máxima velocidad
- ✅ El presupuesto es ajustado
- ✅ Solo necesitas análisis básico
- ✅ Volumen muy alto de eventos

---

## 🚀 Cómo cambiar entre agentes

### De Gemini a Claude

```bash
# 1. Obtener API key
# Ve a: https://console.anthropic.com
# Copia: sk-ant-xxxxxxxxxxxxx

# 2. Actualizar .env
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# 3. Cambiar agent
# Gemini:
python agent/rabbitmq_consumer.py

# Claude:
python agent/claude_agent.py
```

### De Claude a Gemini

```bash
# 1. Obtener API key
# Ve a: https://ai.google.dev/
# Copia tu API key

# 2. Actualizar .env
export GEMINI_API_KEY=xxxxxxxxxxxxx
export MODEL_NAME=gemini-2.0-flash

# 3. Iniciar Gemini Agent
python agent/rabbitmq_consumer.py
```

---

## 📈 Ejemplo de Output

### Entrada (mismo evento para ambos)

```json
{
  "event_type": "SECURITY_EVENT",
  "severity": "HIGH",
  "user_id": "attacker",
  "data": {"ip": "192.168.1.100", "attempts": 6},
  "description": "6 failed login attempts"
}
```

### Claude Output

```
THREAT ASSESSMENT: HIGH RISK
═════════════════════════════
This represents a clear and immediate threat requiring immediate action.

ROOT CAUSE ANALYSIS:
1. Automated brute force attack detected
2. Attacker using credential guessing or dictionary attack
3. High failure count suggests systematic approach

IMMEDIATE ACTIONS:
1. Lock account immediately
2. Review logs from 192.168.1.100 for last 24h
3. Alert security team

LONG-TERM PREVENTION:
1. Implement CAPTCHA after 3 failed attempts
2. Add IP-based rate limiting
3. Enable MFA for all users
4. Geo-IP blocking for suspicious locations

IMPACT: Potential account compromise - IMMEDIATE RESPONSE REQUIRED
```

### Gemini Output

```
Security Alert: Multiple failed login attempts detected
User: attacker | Attempts: 6 | Status: Account recommended lock
Risk Level: HIGH
Action: Lock account and review logs
```

---

## 💡 Ventajas de Cada Uno

### Claude Advantages
✅ Análisis más estructurado y detallado
✅ Mejora continuamente (más reciente)
✅ Excelente para reportes profesionales
✅ Razonamiento más profundo
✅ Mejor manejo de contexto complejo

### Gemini Advantages
✅ Más rápido (~1-2 segundos)
✅ Más barato (10x menos)
✅ Bueno para análisis rápido
✅ Modelo muy optimizado
✅ Integración más fácil

---

## 🔧 Instalación

### Claude Agent

```bash
cd agent

# Virtual environment
python -m venv venv
source venv/bin/activate

# Instalar
pip install anthropic python-dotenv pika

# Configurar
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" >> .env

# Ejecutar
python claude_agent.py
```

### Gemini Agent

```bash
cd agent

# Virtual environment
python -m venv venv
source venv/bin/activate

# Instalar
pip install google-genai python-dotenv pika

# Configurar
echo "GEMINI_API_KEY=xxxxx" >> .env
echo "MODEL_NAME=gemini-2.0-flash" >> .env

# Ejecutar
python rabbitmq_consumer.py
```

---

## 📊 Costo Estimado por 1000 eventos

### Claude
- Análisis típico: ~800 tokens entrada + ~400 tokens salida
- Costo por evento: ~$0.0085
- 1000 eventos: ~$8.50

### Gemini
- Análisis típico: ~800 tokens entrada + ~400 tokens salida
- Costo por evento: ~$0.0003
- 1000 eventos: ~$0.30

---

## 🎓 Recomendación Final

**Para Producción**: Usa **Claude** 🏆
- Reportes profesionales
- Análisis de mejor calidad
- Vale los $8-9 adicionales mensuales
- Empresas gastan mucho más en false positives

**Para Testing/Demo**: Usa **Gemini**
- Es gratis hasta ciertos límites
- Suficientemente bueno para pruebas
- Más rápido para ciclos de desarrollo

**Híbrido**: Usa ambos
```python
if event_severity == "CRITICAL":
    use_claude()  # Análisis profundo
else:
    use_gemini()  # Análisis rápido
```

---

## 📞 Soporte

**Claude Documentation**: https://docs.anthropic.com
**Gemini Documentation**: https://ai.google.dev/docs

**API Consoles**:
- Claude: https://console.anthropic.com
- Gemini: https://ai.google.dev/

---

**Nostromus v0.1.0** - Dual AI Agent Support ✅
