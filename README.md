# 🏥 Compliance Monitor · Sofgen Pharma

Sistema web de gestión de cronograma para el despliegue del SM (Sistema de Monitoreo).  
Multi-usuario · Roles · Persistencia en nube · Streamlit + Supabase

---

## 📋 Tabla de contenidos

1. [Estructura del proyecto](#estructura)
2. [Prerequisitos](#prerequisitos)
3. [Configuración de Supabase](#supabase)
4. [Instalación local](#local)
5. [Publicación en GitHub](#github)
6. [Despliegue en Streamlit Cloud](#streamlit-cloud)
7. [Crear el primer usuario administrador](#primer-usuario)
8. [Guía de uso](#uso)

---

## 📁 Estructura del proyecto {#estructura}

```
compliance-monitor/
├── .streamlit/
│   ├── config.toml          ← Tema Sofgen (colores, fuente)
│   └── secrets.toml.example ← Plantilla de variables de entorno
├── app/
│   ├── auth.py              ← Autenticación Supabase
│   ├── components.py        ← Componentes UI reutilizables
│   ├── database.py          ← Todas las consultas a Supabase
│   ├── models.py            ← Modelos de datos y constantes
│   ├── styles.py            ← CSS del sistema de diseño
│   └── utils.py             ← Funciones auxiliares
├── pages/
│   ├── 1_Dashboard.py       ← KPIs y semáforos en tiempo real
│   ├── 2_Cronograma.py      ← Tabla editable de actividades
│   ├── 3_Gantt.py           ← Diagrama de Gantt interactivo
│   └── 4_Configuracion.py   ← Fecha inicio, escenario, perfil
├── assets/
│   └── logo_sofgen.jpg      ← Logo Sofgen Pharma
├── sql/
│   └── schema.sql           ← Schema completo + 50 actividades seed
├── main.py                  ← Página de login
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ✅ Prerequisitos {#prerequisitos}

- Python 3.11 o superior
- Cuenta en [Supabase](https://supabase.com) (plan gratuito funciona para desarrollo)
- Cuenta en [GitHub](https://github.com)
- Cuenta en [Streamlit Cloud](https://share.streamlit.io) (gratuita)
- Git instalado en tu máquina

---

## 🗄️ Configuración de Supabase {#supabase}

### Paso 1 — Crear proyecto

1. Ve a [supabase.com](https://supabase.com) → **New project**
2. Nombre: `compliance-monitor`
3. Contraseña de BD: guárdala en un lugar seguro
4. Región: **South America (São Paulo)** o US East
5. Plan: **Free** (suficiente para desarrollo) o **Pro** para producción

### Paso 2 — Ejecutar el schema SQL

1. En el panel de Supabase → **SQL Editor** → **New query**
2. Abre el archivo `sql/schema.sql` de este proyecto
3. Copia todo el contenido y pégalo en el editor
4. Clic en **Run** (▶)
5. Verifica en **Table Editor** que existen las tablas:
   - `profiles`
   - `project_config`
   - `activities`
   - `activity_log`
   - `user_notes`

### Paso 3 — Obtener credenciales

1. Panel de Supabase → **Project Settings** → **API**
2. Copia:
   - **Project URL** → `https://xxxx.supabase.co`
   - **anon public key** → llave que empieza con `eyJ...`

> ⚠️ Nunca uses la `service_role` key en el frontend. Solo la `anon` key.

---

## 💻 Instalación local {#local}

```bash
# 1. Clona o descarga el proyecto
cd compliance-monitor/

# 2. Crea entorno virtual
python -m venv .venv

# En Windows:
.venv\Scripts\activate
# En Mac/Linux:
source .venv/bin/activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Crea el archivo de secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edita `.streamlit/secrets.toml` con tus credenciales de Supabase:

```toml
SUPABASE_URL = "https://tu-proyecto.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

```bash
# 5. Ejecuta la app
streamlit run main.py
```

La app abre en `http://localhost:8501`

---

## 🐙 Publicación en GitHub {#github}

```bash
# En la carpeta del proyecto:
git init
git add .
git commit -m "feat: initial commit - Compliance Monitor Sofgen Pharma"

# Crea un repositorio en github.com (puede ser privado)
# Luego conecta y sube:
git remote add origin https://github.com/TU_USUARIO/compliance-monitor.git
git branch -M main
git push -u origin main
```

> ⚠️ Confirma que `.gitignore` excluye `.streamlit/secrets.toml`  
> antes de hacer push. **Nunca** subas tus credenciales a GitHub.

---

## 🚀 Despliegue en Streamlit Cloud {#streamlit-cloud}

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. **New app**
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Repository:** `TU_USUARIO/compliance-monitor`
   - **Branch:** `main`
   - **Main file path:** `main.py`
5. Clic en **Advanced settings** → **Secrets**
6. Pega las variables de entorno:
   ```toml
   SUPABASE_URL = "https://tu-proyecto.supabase.co"
   SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```
7. **Deploy!**

En 2-3 minutos tendrás una URL pública como:  
`https://compliance-monitor-sofgen.streamlit.app`

---

## 👑 Crear el primer usuario administrador {#primer-usuario}

Después del despliegue, el primer usuario debe crearse manualmente en Supabase para asignarle el rol `administrador`.

### Opción A — Invitación por email (recomendado)

1. Panel Supabase → **Authentication** → **Users** → **Invite user**
2. Ingresa el email del administrador
3. El usuario recibirá un link para crear su contraseña

### Opción B — Crear usuario directo

1. Panel Supabase → **Authentication** → **Users** → **Add user**
2. Email + contraseña

### Asignar rol administrador

Después de crear el usuario, ejecuta en **SQL Editor**:

```sql
-- Reemplaza el email con el del administrador
UPDATE public.profiles
SET role = 'administrador'
WHERE email = 'admin@sofgen.com';
```

### Crear usuarios adicionales

Repite el proceso para cada analista y supervisor. Para asignar roles:

```sql
-- Supervisor
UPDATE public.profiles SET role = 'supervisor' WHERE email = 'supervisor@sofgen.com';

-- Analista (rol por defecto, no es necesario UPDATE)
UPDATE public.profiles SET role = 'analista' WHERE email = 'analista@sofgen.com';
```

O usa la pestaña **⚙️ Configuración → Usuarios** dentro de la app (solo visible para administradores).

---

## 📖 Guía de uso {#uso}

### Flujo de trabajo recomendado

```
1. Admin configura fecha de inicio → Configuración ⚙️
2. Admin selecciona escenario (SQL Server o Supabase)
3. Supervisor actualiza estados a medida que avanza el proyecto
4. Equipo monitorea el dashboard en tiempo real
```

### Roles y permisos

| Acción | Analista | Supervisor | Administrador |
|---|:---:|:---:|:---:|
| Ver Dashboard | ✅ | ✅ | ✅ |
| Ver Cronograma | ✅ | ✅ | ✅ |
| Ver Gantt | ✅ | ✅ | ✅ |
| Agregar notas personales | ✅ | ✅ | ✅ |
| Actualizar estados de actividades | ❌ | ✅ | ✅ |
| Configurar fecha inicio / escenario | ❌ | ✅ | ✅ |
| Gestionar usuarios y roles | ❌ | ❌ | ✅ |

### Páginas de la app

| Página | Descripción |
|---|---|
| **📊 Dashboard** | KPIs globales, semáforo por fase, gráficos de progreso |
| **📋 Cronograma** | Tabla editable con filtros; cambio de estado inline |
| **📅 Gantt** | Diagrama de barras horizontal; colorear por estado o responsable |
| **⚙️ Configuración** | Fecha inicio, escenario, perfil, historial y usuarios |

### Estados de actividad

| Estado | Descripción |
|---|---|
| ⚪ **PENDIENTE** | Actividad no iniciada |
| 🟡 **EN PROGRESO** | Actividad en ejecución |
| ✅ **COMPLETADO** | Actividad finalizada |

---

## 🔧 Solución de problemas

**Error: `KeyError: 'SUPABASE_URL'`**  
→ Verifica que `secrets.toml` existe en `.streamlit/` y tiene las dos variables.

**Error: `Invalid login credentials`**  
→ Verifica que el usuario existe en Supabase → Authentication → Users.

**La tabla `activities` está vacía**  
→ Re-ejecuta `sql/schema.sql` en el SQL Editor de Supabase.

**El rol del usuario no se actualiza**  
→ Ejecuta el UPDATE en el SQL Editor directamente con el email correcto.

**Las fechas del Gantt muestran "2024-01-XX"**  
→ Normal: es el modo sin fecha inicio. Define la fecha en ⚙️ Configuración.

---

## 📞 Soporte técnico

- **Desarrollado por:** Área de Cumplimiento Legal Corporativo · Sofgen Pharma
- **Stack:** Python 3.11 · Streamlit 1.32+ · Supabase (PostgreSQL) · Plotly
- **Versión:** 1.0.0 · Mayo 2026
