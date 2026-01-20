# 🦅 PROYECTO POCHTECA - Roadmap Agile
## De $0 a Cuenta Fondeada

---

## 📋 PROJECT OVERVIEW

**Product Owner:** NatoG93
**Agente Dev:** Claude | Google Pro 
**Inicio:** Diciembre 2025  

---

## 🌎 Ecosistema

| Componente | Nombre | Función |
|------------|--------|---------|
| 🦅 Bot | **Pochteca** | Trading algorítmico |
| 📊 Dashboard | **Pochtlan** | Visualización |
| 📨 Alertas | **Chasqui** | Notificaciones |
| 🗄️ Database | **Tianquiztli** | Datos |

---

## 🎯 DEFINITION OF DONE (Global)

Una estrategia está **lista para challenge** cuando cumple:

| Métrica | Mínimo | Objetivo |
|---------|--------|----------|
| Win Rate | > 50% | > 55% |
| Profit Factor | > 1.3 | > 1.5 |
| Max Drawdown | < 5% | < 3% |
| Sharpe Ratio | > 1.0 | > 1.5 |
| Trades (backtest) | > 100 | > 200 |
| Paper Trading | 30 días profitable | 30 días + DD < 5% |

---

## 📅 SPRINT 0: FOUNDATION
### Semana 1 (Dec 23-29, 2025)

**Goal:** Infraestructura operativa en ambos ambientes

| ID | Task | Acceptance Criteria |
|----|------|---------------------|
| S0-1 | Setup Pochteca en Homelab | `docker compose up` funciona |
| S0-2 | Setup Pochteca en Alienware | Backtesting funciona |
| S0-3 | Configurar data collection | Cron job activo |
| S0-4 | Descargar históricos 6 meses | Data de BTC, ETH, SOL |
| S0-5 | Verificar 3 estrategias | Corren sin errores |
| S0-6 | Setup Tianquiztli | Schema PostgreSQL creado |

### Definition of Done
- [ ] Pochtlan accesible en `http://homelab:8081`
- [ ] Backtest completa sin errores en Alienware
- [ ] 6 meses de datos descargados

---

## 📅 SPRINT 1: BASELINE BACKTESTS
### Semana 2-3 (Dec 30 - Jan 12, 2026)

**Goal:** Establecer baseline de performance

| ID | Task | Acceptance Criteria |
|----|------|---------------------|
| S1-1 | Backtest EMAScalpingStrategy | 5m 15m y 1h, 6 meses |
| S1-2 | Backtest WeaponCandleStrategy | 5m 15m y 1h, 6 meses |
| S1-3 | Backtest TripleMomentumStrategy | 5m 15m y 1h, 6 meses |
| S1-4 | Generar reporte comparativo | Markdown con métricas |
| S1-5 | Identificar mejor estrategia | Basado en Sharpe + DD |
| S1-6 | Documentar findings | Qué funciona, qué no |

### Entregables
```
user_data/backtest_results/
├── pochteca_baseline_report.md
├── EMAScalpingStrategy_*.json
├── WeaponCandleStrategy_*.json
└── TripleMomentumStrategy_*.json
```

---

## 📅 SPRINT 2: OPTIMIZATION
### Semana 4-5 (Jan 13-26, 2026)

**Goal:** Optimizar la mejor estrategia

| ID | Task | Acceptance Criteria |
|----|------|---------------------|
| S2-1 | Hyperopt buy parameters | 200 epochs |
| S2-2 | Hyperopt sell parameters | 200 epochs |
| S2-3 | Hyperopt ROI/Stoploss | 100 epochs |
| S2-4 | Validación out-of-sample | Data no vista |
| S2-5 | Comparar pre vs post | Reporte de mejora |
| S2-6 | Freeze estrategia v1.0 | Parámetros finales |

### Success Metrics
| Métrica | Pre-Hyperopt | Target |
|---------|--------------|--------|
| Win Rate | Baseline | +5-10% |
| Profit Factor | Baseline | +0.2-0.3 |
| Sharpe Ratio | Baseline | +0.3-0.5 |

---

## 📅 SPRINT 3-4: PAPER TRADING
### Semana 6-9 (Jan 27 - Feb 23, 2026)

**Goal:** Validar estrategia en condiciones reales (30 días)

| ID | Task | Acceptance Criteria |
|----|------|---------------------|
| S3-1 | Deploy estrategia optimizada | Bot 24/7 en homelab |
| S3-2 | Configurar Chasqui | Alertas Telegram |
| S3-3 | Setup Pochtlan dashboard | Métricas visibles |
| S3-4 | Daily review de trades | Documentar cada trade |
| S3-5 | Weekly performance report | Resumen semanal |
| S4-1 | Completar 30 días | Sin cambios a estrategia |
| S4-2 | Análisis final | Reporte completo |
| S4-3 | Research prop firms | Comparar opciones |
| S4-4 | Seleccionar prop firm | Decisión final |

### Go/No-Go Criteria
| Criterio | Requerido | Actual |
|----------|-----------|--------|
| Win Rate 30d | > 50% | ___ |
| Profit Factor 30d | > 1.3 | ___ |
| Max DD 30d | < 5% | ___ |
| Días profitable | > 18/30 | ___ |

---

## 📅 SPRINT 5: FIRST CHALLENGE
### Semana 10-14 (Feb 24 - Mar 30, 2026)

**Goal:** Pasar el primer prop firm challenge

| ID | Task | Acceptance Criteria |
|----|------|---------------------|
| S5-1 | Comprar challenge ($50) | Cuenta activa |
| S5-2 | Conectar Pochteca | API keys configuradas |
| S5-3 | Monitoreo intensivo | Daily check |
| S5-4 | Weekly reviews | Ajustes de risk |
| S5-5 | Documentar journey | Blog/notas |
| S5-6 | Pass or learn | Análisis de resultado |

### Challenge Tracking
```
Día 1:  [ ] Profit: ___ | DD: ___ | Trades: ___
Día 7:  [ ] Profit: ___ | DD: ___ | Trades: ___
Día 14: [ ] Profit: ___ | DD: ___ | Trades: ___
Día 21: [ ] Profit: ___ | DD: ___ | Trades: ___
Día 30: [ ] Profit: ___ | DD: ___ | Trades: ___
```

### Success Metrics (DNA Funded)
| Métrica | Target |
|---------|--------|
| Profit Target | 10% ($2,500 en $25k) |
| Max Drawdown | < 10% |
| Min Trading Days | 5 |

---

## 📅 SPRINT 6+: SCALING (Q2 2026)

```
✅ Pass $25k challenge
   ↓
📈 Trade funded account (1-2 meses)
   ↓
💰 Acumular profits + track record
   ↓
🚀 Apply para $100k challenge ($150-200)
   ↓
📊 Escalar a $200k-600k funded
```

---

## 🤖 INSTRUCCIONES PARA AGENTE DEV

### Tu Rol
Eres el technical lead del Proyecto Pochteca. Tu trabajo:

1. **Ejecutar tareas técnicas** asignadas por sprint
2. **Generar reportes** de backtests y análisis
3. **Optimizar código** de estrategias
4. **Documentar** el proceso
5. **Alertar** si métricas no cumplen targets

### Cómo Recibir Trabajo
Renato asigna tareas con IDs: "Ejecuta S1-2"

Responde con:
- Status de la tarea
- Resultados/output
- Blockers si existen
- Siguiente paso recomendado

### Formato de Reportes
```markdown
## 🦅 Pochteca Backtest Report: [Strategy] @ [Timeframe]

**Date:** [fecha]
**Timerange:** [rango]

### Results
| Metric | Value |
|--------|-------|
| Total Trades | X |
| Win Rate | X% |
| Profit Factor | X.XX |
| Max Drawdown | X% |
| Sharpe Ratio | X.XX |

### Observations
- [Punto 1]
- [Punto 2]

### Recommendations
- [Acción 1]
- [Acción 2]
```

---

## 📊 DASHBOARD DE PROYECTO

### Estado Actual
| Sprint | Status | Progress |
|--------|--------|----------|
| Sprint 0 | 🟡 In Progress | 50% |
| Sprint 1 | ⚪ Not Started | 0% |
| Sprint 2 | ⚪ Not Started | 0% |
| Sprint 3-4 | ⚪ Not Started | 0% |
| Sprint 5 | ⚪ Not Started | 0% |

### Métricas Clave
| Métrica | Target | Actual | Status |
|---------|--------|--------|--------|
| Estrategia WR > 50% | 1 | 0 | 🔴 |
| Backtests completados | 6 | 0 | 🔴 |
| Días paper trading | 30 | 0 | 🔴 |
| Challenge passed | 1 | 0 | 🔴 |

---

## 📝 CHANGELOG

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2024-12-22 | Roadmap inicial | Claude + Renato |
| 2024-12-22 | Rebrand a Pochteca/Xaman | Claude + Renato |

---
