import React, { useState, useEffect } from "react";
import { useKeycloak } from "@react-keycloak/web";
import "./DecisionPanel.css";

const DecisionPanel = () => {
  const { keycloak } = useKeycloak();
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [decision, setDecision] = useState(null);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(true);
  const [processedCount, setProcessedCount] = useState(0);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    // Extraer información del usuario actual
    if (keycloak?.tokenParsed) {
      setCurrentUser({
        username: keycloak.tokenParsed.preferred_username,
        email: keycloak.tokenParsed.email,
        name: keycloak.tokenParsed.name
      });
    }

    fetchPendingEvents();
  }, [keycloak]);

  const fetchPendingEvents = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/decisions/pending-events");
      const data = await response.json();
      setEvents(data.events || []);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching events:", error);
      setLoading(false);
    }
  };

  const handleDecision = async () => {
    if (!decision || !selectedEvent) return;

    try {
      const headers = {
        "Content-Type": "application/json"
      };

      // Agregar token de Keycloak si está disponible
      if (keycloak?.token) {
        headers["Authorization"] = `Bearer ${keycloak.token}`;
      }

      const response = await fetch("http://localhost:8000/api/decisions/decide", {
        method: "POST",
        headers,
        body: JSON.stringify({
          event_id: selectedEvent.id,
          decision: decision,
          notes: notes,
          analyst_username: currentUser?.username || "unknown"
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Actualizar contadores
        setProcessedCount(prev => prev + 1);

        // Remover evento de la lista
        setEvents(events.filter(e => e.id !== selectedEvent.id));

        // Resetear selección
        setSelectedEvent(null);
        setDecision(null);
        setNotes("");

        alert(`✓ Decisión procesada por ${data.analyst}!\nReporte: ${data.report_id}`);
      }
    } catch (error) {
      console.error("Error processing decision:", error);
      alert("✗ Error al procesar decisión");
    }
  };

  const DECISION_OPTIONS = [
    {
      id: 1,
      label: "🔴 BLOQUEAR & ALERTAR",
      description: "Acción crítica - Bloquear cuenta y alertar al equipo"
    },
    {
      id: 2,
      label: "⚠️ ALERTAR",
      description: "Enviar alerta al equipo de seguridad"
    },
    {
      id: 3,
      label: "🔍 INVESTIGAR",
      description: "Iniciar investigación forense completa"
    },
    {
      id: 4,
      label: "📝 REGISTRAR",
      description: "Solo registrar para referencia futura"
    }
  ];

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: "#ff0000",
      HIGH: "#ff6600",
      MEDIUM: "#ffaa00",
      LOW: "#00aa00"
    };
    return colors[severity] || "#999";
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      CRITICAL: "🔴🔴",
      HIGH: "🔴",
      MEDIUM: "🟡",
      LOW: "🟢"
    };
    return icons[severity] || "❓";
  };

  if (loading) {
    return <div className="decision-panel loading">Cargando eventos...</div>;
  }

  return (
    <div className="decision-panel">
      <div className="decision-header">
        <h1>🤖 Nostromus Decision Panel</h1>
        <p>Threat Analyst - Toma decisiones sobre incidentes</p>
        {currentUser && (
          <div className="user-info">
            <span className="user-badge">
              👤 <strong>{currentUser.name || currentUser.username}</strong> ({currentUser.email})
            </span>
          </div>
        )}
        <div className="stats">
          <span className="stat">
            📊 Eventos pendientes: <strong>{events.length}</strong>
          </span>
          <span className="stat">
            ✅ Procesados: <strong>{processedCount}</strong>
          </span>
        </div>
      </div>

      <div className="decision-container">
        {/* Lista de eventos */}
        <div className="events-list">
          <h2>📋 Eventos Pendientes</h2>

          {events.length === 0 ? (
            <div className="no-events">
              <p>✓ No hay eventos pendientes</p>
              <p>Todos los incidentes han sido revisados</p>
            </div>
          ) : (
            events.map(event => (
              <div
                key={event.id}
                className={`event-card ${selectedEvent?.id === event.id ? "selected" : ""}`}
                onClick={() => setSelectedEvent(event)}
              >
                <div className="event-header">
                  <span className="severity-badge" style={{ color: getSeverityColor(event.severity) }}>
                    {getSeverityIcon(event.severity)} {event.severity}
                  </span>
                  <span className="event-type">{event.type}</span>
                </div>
                <div className="event-content">
                  <p className="description">{event.description}</p>
                  <p className="user">
                    <strong>Usuario:</strong> {event.user_id}
                  </p>
                  <div className="data-preview">
                    {Object.entries(event.data || {}).map(([key, value]) => (
                      <span key={key} className="data-item">
                        <strong>{key}:</strong> {JSON.stringify(value)}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Panel de decisión */}
        <div className="decision-form">
          {selectedEvent ? (
            <>
              <h2>🎯 Toma una Decisión</h2>

              <div className="event-details">
                <h3>{selectedEvent.type}</h3>
                <p>{selectedEvent.description}</p>
              </div>

              <div className="decision-options">
                {DECISION_OPTIONS.map(option => (
                  <button
                    key={option.id}
                    className={`decision-btn ${decision === option.id ? "selected" : ""}`}
                    onClick={() => setDecision(option.id)}
                  >
                    <div className="btn-label">{option.label}</div>
                    <div className="btn-description">{option.description}</div>
                  </button>
                ))}
              </div>

              <div className="notes-section">
                <label>📝 Notas (opcional):</label>
                <textarea
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Agrega notas sobre tu decisión..."
                />
              </div>

              <div className="action-buttons">
                <button
                  className="btn-confirm"
                  onClick={handleDecision}
                  disabled={!decision}
                >
                  ✓ Procesar Decisión
                </button>
                <button
                  className="btn-cancel"
                  onClick={() => {
                    setSelectedEvent(null);
                    setDecision(null);
                    setNotes("");
                  }}
                >
                  ✕ Cancelar
                </button>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>👈 Selecciona un evento para tomar una decisión</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DecisionPanel;
