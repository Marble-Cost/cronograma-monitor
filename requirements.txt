-- ============================================================
-- COMPLIANCE MONITOR · Sofgen Pharma
-- Schema v1.0 · Mayo 2026
-- ============================================================
-- Instrucciones:
--   1. Abre el Editor SQL de tu proyecto Supabase
--   2. Copia y pega todo este archivo
--   3. Ejecuta (Run)
-- ============================================================

-- Extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


-- ============================================================
-- TABLA: profiles
-- Extiende auth.users con nombre completo y rol
-- ============================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email       TEXT        NOT NULL DEFAULT '',
    full_name   TEXT        NOT NULL DEFAULT '',
    role        TEXT        NOT NULL DEFAULT 'analista'
                            CHECK (role IN ('analista', 'supervisor', 'administrador')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger: crea perfil automáticamente al registrar usuario
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, role)
    VALUES (
        NEW.id,
        COALESCE(NEW.email, ''),
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'role', 'analista')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();


-- ============================================================
-- TABLA: project_config
-- Configuración global del proyecto (fecha inicio, escenario)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.project_config (
    id           SERIAL      PRIMARY KEY,
    project_name TEXT        NOT NULL DEFAULT 'Compliance Monitor · Sofgen Pharma',
    start_date   DATE,
    scenario     TEXT        NOT NULL DEFAULT 'Supabase'
                             CHECK (scenario IN ('SQL Server', 'Supabase')),
    total_weeks  INTEGER     NOT NULL DEFAULT 12,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Registro inicial (solo debe existir uno)
INSERT INTO public.project_config (project_name, start_date, scenario, total_weeks)
VALUES ('Compliance Monitor · Sofgen Pharma', NULL, 'Supabase', 12)
ON CONFLICT DO NOTHING;


-- ============================================================
-- TABLA: activities
-- Las 25 actividades por escenario (50 en total)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.activities (
    id               SERIAL      PRIMARY KEY,
    scenario         TEXT        NOT NULL CHECK (scenario IN ('SQL Server', 'Supabase')),
    fase_number      INTEGER     NOT NULL CHECK (fase_number BETWEEN 0 AND 4),
    fase_name        TEXT        NOT NULL,
    activity_number  INTEGER     NOT NULL CHECK (activity_number BETWEEN 1 AND 25),
    activity_name    TEXT        NOT NULL,
    responsable      TEXT        NOT NULL CHECK (responsable IN ('Desarrollador', 'TI', 'Ambos', 'Liderazgo')),
    status           TEXT        NOT NULL DEFAULT 'PENDIENTE'
                                 CHECK (status IN ('PENDIENTE', 'EN PROGRESO', 'COMPLETADO')),
    week_start       INTEGER     NOT NULL CHECK (week_start BETWEEN 1 AND 12),
    week_end         INTEGER     NOT NULL CHECK (week_end BETWEEN 1 AND 12),
    notes            TEXT        NOT NULL DEFAULT '',
    updated_by       UUID        REFERENCES auth.users(id) ON DELETE SET NULL,
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_scenario_activity UNIQUE (scenario, activity_number)
);


-- ============================================================
-- TABLA: activity_log
-- Auditoría inmutable de cambios de estado
-- ============================================================
CREATE TABLE IF NOT EXISTS public.activity_log (
    id           SERIAL      PRIMARY KEY,
    activity_id  INTEGER     NOT NULL REFERENCES public.activities(id) ON DELETE CASCADE,
    user_id      UUID        REFERENCES auth.users(id) ON DELETE SET NULL,
    user_email   TEXT,
    old_status   TEXT,
    new_status   TEXT        NOT NULL,
    changed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
-- TABLA: user_notes
-- Notas privadas por usuario por actividad
-- ============================================================
CREATE TABLE IF NOT EXISTS public.user_notes (
    id           SERIAL      PRIMARY KEY,
    activity_id  INTEGER     NOT NULL REFERENCES public.activities(id) ON DELETE CASCADE,
    user_id      UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    note         TEXT        NOT NULL DEFAULT '',
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_note_per_user_activity UNIQUE (activity_id, user_id)
);


-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- profiles --
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "profiles_select_own"
    ON public.profiles FOR SELECT TO authenticated
    USING (id = auth.uid());

CREATE POLICY "profiles_update_own"
    ON public.profiles FOR UPDATE TO authenticated
    USING (id = auth.uid()) WITH CHECK (id = auth.uid());

-- Permite al admin leer todos los perfiles
CREATE POLICY "profiles_select_admin"
    ON public.profiles FOR SELECT TO authenticated
    USING (
        auth.uid() IN (
            SELECT id FROM public.profiles WHERE role = 'administrador'
        )
    );

-- Permite al admin actualizar roles
CREATE POLICY "profiles_update_admin"
    ON public.profiles FOR UPDATE TO authenticated
    USING (
        auth.uid() IN (
            SELECT id FROM public.profiles WHERE role = 'administrador'
        )
    );

-- project_config --
ALTER TABLE public.project_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "config_select_authenticated"
    ON public.project_config FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "config_update_editors"
    ON public.project_config FOR UPDATE TO authenticated
    USING (
        auth.uid() IN (
            SELECT id FROM public.profiles
            WHERE role IN ('administrador', 'supervisor')
        )
    );

-- activities --
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "activities_select_authenticated"
    ON public.activities FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "activities_update_editors"
    ON public.activities FOR UPDATE TO authenticated
    USING (
        auth.uid() IN (
            SELECT id FROM public.profiles
            WHERE role IN ('administrador', 'supervisor')
        )
    );

-- activity_log --
ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "log_select_authenticated"
    ON public.activity_log FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "log_insert_authenticated"
    ON public.activity_log FOR INSERT TO authenticated
    WITH CHECK (true);

-- user_notes --
ALTER TABLE public.user_notes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "notes_own_user"
    ON public.user_notes FOR ALL TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());


-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_activities_scenario
    ON public.activities(scenario);

CREATE INDEX IF NOT EXISTS idx_activities_fase
    ON public.activities(scenario, fase_number);

CREATE INDEX IF NOT EXISTS idx_log_activity
    ON public.activity_log(activity_id, changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_notes_user
    ON public.user_notes(user_id, activity_id);


-- ============================================================
-- SEED DATA — Escenario: SQL Server (25 actividades)
-- ============================================================
INSERT INTO public.activities
    (scenario, fase_number, fase_name, activity_number, activity_name, responsable, week_start, week_end, notes)
VALUES
-- FASE 0 · Alineación y Arranque
('SQL Server', 0, 'FASE 0 · Alineación y Arranque',  1,
 'Reunión de arranque con TI y liderazgo',
 'Ambos', 1, 1,
 'Presentar alcance, requerimientos de servidor y cronograma'),

('SQL Server', 0, 'FASE 0 · Alineación y Arranque',  2,
 'TI asigna servidor y configura red interna',
 'TI', 1, 2,
 'Servidor Windows Server o Linux con acceso LAN. ⚠️ DEPENDENCIA CRÍTICA'),

('SQL Server', 0, 'FASE 0 · Alineación y Arranque',  3,
 'TI instala SQL Server en el servidor',
 'TI', 2, 2,
 'SQL Server 2019 o superior. ⚠️ DEPENDENCIA CRÍTICA'),

('SQL Server', 0, 'FASE 0 · Alineación y Arranque',  4,
 'TI asigna URL interna (ej: cumplimiento.empresa.com)',
 'TI', 2, 2,
 'DNS interno o IP fija accesible desde la red corporativa'),

('SQL Server', 0, 'FASE 0 · Alineación y Arranque',  5,
 'TI habilita credenciales de acceso al servidor',
 'TI', 2, 2,
 'Usuario de servicio con permisos de creación de BD'),

-- FASE 1 · Base de Datos SQL Server
('SQL Server', 1, 'FASE 1 · Base de Datos',  6,
 'Diseño del esquema de tablas',
 'Desarrollador', 2, 3,
 'Tablas: Usuarios, Terceros, Alertas, Decisiones Privadas, Decisiones Publicadas, Historial'),

('SQL Server', 1, 'FASE 1 · Base de Datos',  7,
 'Creación de la base de datos COMPLIANCE_MONITOR_DB',
 'Desarrollador', 3, 3,
 'Script SQL de creación de tablas y relaciones'),

('SQL Server', 1, 'FASE 1 · Base de Datos',  8,
 'Configuración de roles y permisos',
 'Desarrollador', 3, 4,
 'Roles: Analista, Supervisor, Administrador'),

('SQL Server', 1, 'FASE 1 · Base de Datos',  9,
 'Implementación de Row Level Security (RLS)',
 'Desarrollador', 4, 4,
 'Políticas RLS para espacio privado por analista'),

('SQL Server', 1, 'FASE 1 · Base de Datos', 10,
 'Configuración de tabla inmutable de decisiones',
 'Desarrollador', 4, 4,
 'Restricción UPDATE/DELETE para terceros. Solo propietario puede editar'),

('SQL Server', 1, 'FASE 1 · Base de Datos', 11,
 'Pruebas de aislamiento entre usuarios',
 'Desarrollador', 4, 4,
 'Verificar que usuario A no ve datos de usuario B'),

-- FASE 2 · Backend Python
('SQL Server', 2, 'FASE 2 · Backend Python', 12,
 'Reemplazar SQLite por SQL Server en los 3 módulos',
 'Desarrollador', 4, 5,
 'pyodbc / SQLAlchemy. Migrar SMT, ARC y AMP'),

('SQL Server', 2, 'FASE 2 · Backend Python', 13,
 'Adaptar lectura de Excel SAP (sin cambio de columnas)',
 'Desarrollador', 5, 6,
 'Archivo de mapeo JSON: nombre SAP → nombre interno COMPLIANCE MONITOR'),

('SQL Server', 2, 'FASE 2 · Backend Python', 14,
 'Desarrollar sistema de autenticación y sesiones',
 'Desarrollador', 6, 6,
 'Login, token de sesión, cierre automático por inactividad'),

('SQL Server', 2, 'FASE 2 · Backend Python', 15,
 'Desarrollar API de decisiones compartidas',
 'Desarrollador', 6, 7,
 'Endpoints para publicar, leer y (solo propietario) editar decisiones'),

('SQL Server', 2, 'FASE 2 · Backend Python', 16,
 'Desarrollar tablero compartido del equipo',
 'Desarrollador', 7, 7,
 'Vista de feed de decisiones publicadas por todos los analistas'),

-- FASE 3 · Frontend y Seguridad
('SQL Server', 3, 'FASE 3 · Frontend y Seguridad', 17,
 'Pantalla de inicio de sesión',
 'Desarrollador', 7, 8,
 'Login corporativo con validación de credenciales contra SQL Server'),

('SQL Server', 3, 'FASE 3 · Frontend y Seguridad', 18,
 'Adaptar dashboards HTML para múltiples usuarios',
 'Desarrollador', 8, 8,
 'Cada analista ve solo su espacio. Tablero compartido visible para todos'),

('SQL Server', 3, 'FASE 3 · Frontend y Seguridad', 19,
 'Pruebas de seguridad y penetración básica',
 'Ambos', 8, 9,
 'Verificar RLS, tokens, acceso no autorizado. Participación de TI recomendada'),

('SQL Server', 3, 'FASE 3 · Frontend y Seguridad', 20,
 'Auditoría de trazabilidad: verificar historial de sesiones',
 'Desarrollador', 9, 9,
 'Confirmar que cada acción queda registrada con usuario, fecha y hora'),

-- FASE 4 · Testing y Despliegue
('SQL Server', 4, 'FASE 4 · Testing y Despliegue', 21,
 'Pruebas integrales con datos reales SAP',
 'Desarrollador', 9, 10,
 'Ejecutar el sistema completo con el Excel real de SAP en el servidor'),

('SQL Server', 4, 'FASE 4 · Testing y Despliegue', 22,
 'Pruebas de usuario con el equipo de cumplimiento',
 'Ambos', 10, 11,
 'Los 4-5 analistas prueban el sistema en condiciones reales'),

('SQL Server', 4, 'FASE 4 · Testing y Despliegue', 23,
 'Correcciones post-pruebas de usuario',
 'Desarrollador', 11, 11,
 'Ajustes de UX, errores detectados, calibración de alertas'),

('SQL Server', 4, 'FASE 4 · Testing y Despliegue', 24,
 'Despliegue final en servidor corporativo',
 'Ambos', 11, 12,
 'TI confirma disponibilidad en red. URL activa para todos los usuarios'),

('SQL Server', 4, 'FASE 4 · Testing y Despliegue', 25,
 'Entrega formal y capacitación al equipo',
 'Ambos', 12, 12,
 'Sesión de capacitación. Entrega de manual de usuario básico')

ON CONFLICT (scenario, activity_number) DO NOTHING;


-- ============================================================
-- SEED DATA — Escenario: Supabase (25 actividades)
-- ============================================================
INSERT INTO public.activities
    (scenario, fase_number, fase_name, activity_number, activity_name, responsable, week_start, week_end, notes)
VALUES
-- FASE 0 · Alineación y Aprobación
('Supabase', 0, 'FASE 0 · Alineación y Aprobación',  1,
 'Reunión de arranque con TI y liderazgo',
 'Ambos', 1, 1,
 'Presentar alcance, política de datos en la nube y cronograma'),

('Supabase', 0, 'FASE 0 · Alineación y Aprobación',  2,
 'Validación legal y de seguridad de Supabase (TI + Jurídica)',
 'TI', 1, 2,
 'Revisar política de datos en nube externa. ⚠️ DEPENDENCIA CRÍTICA'),

('Supabase', 0, 'FASE 0 · Alineación y Aprobación',  3,
 'Aprobación formal del plan Equipo o Empresa de Supabase',
 'Liderazgo', 2, 2,
 'Contratación del plan y activación de la cuenta corporativa'),

('Supabase', 0, 'FASE 0 · Alineación y Aprobación',  4,
 'Configuración del proyecto en Supabase',
 'Desarrollador', 2, 2,
 'Crear proyecto, región (preferiblemente US-East o EU), variables de entorno'),

('Supabase', 0, 'FASE 0 · Alineación y Aprobación',  5,
 'TI asigna URL interna o configura proxy hacia Supabase',
 'TI', 2, 2,
 'Opcional: proxy inverso para URL interna aunque BD esté en nube'),

-- FASE 1 · Base de Datos Supabase
('Supabase', 1, 'FASE 1 · Base de Datos Supabase',  6,
 'Diseño del esquema de tablas en Supabase',
 'Desarrollador', 2, 3,
 'Tablas: Usuarios, Terceros, Alertas, Decisiones Privadas, Decisiones Publicadas, Historial'),

('Supabase', 1, 'FASE 1 · Base de Datos Supabase',  7,
 'Creación de tablas vía editor SQL de Supabase',
 'Desarrollador', 3, 3,
 'Supabase tiene editor SQL visual — no requiere acceso a servidor'),

('Supabase', 1, 'FASE 1 · Base de Datos Supabase',  8,
 'Configuración de roles con Auth de Supabase',
 'Desarrollador', 3, 4,
 'Roles: Analista, Supervisor, Admin. Supabase Auth viene integrado'),

('Supabase', 1, 'FASE 1 · Base de Datos Supabase',  9,
 'Implementación de Row Level Security (RLS) en PostgreSQL',
 'Desarrollador', 4, 4,
 'Políticas RLS nativas de PostgreSQL. Más ágil que SQL Server'),

('Supabase', 1, 'FASE 1 · Base de Datos Supabase', 10,
 'Configuración de tabla inmutable de decisiones',
 'Desarrollador', 4, 4,
 'Trigger PostgreSQL que impide edición por terceros'),

('Supabase', 1, 'FASE 1 · Base de Datos Supabase', 11,
 'Pruebas de aislamiento entre usuarios',
 'Desarrollador', 4, 4,
 'Verificar que usuario A no ve datos de usuario B'),

-- FASE 2 · Backend Python
('Supabase', 2, 'FASE 2 · Backend Python', 12,
 'Reemplazar SQLite por Supabase en los 3 módulos',
 'Desarrollador', 4, 5,
 'supabase-py (cliente oficial). Migrar SMT, ARC y AMP'),

('Supabase', 2, 'FASE 2 · Backend Python', 13,
 'Adaptar lectura de Excel SAP (sin cambio de columnas)',
 'Desarrollador', 5, 6,
 'Archivo de mapeo JSON: nombre SAP → nombre interno COMPLIANCE MONITOR'),

('Supabase', 2, 'FASE 2 · Backend Python', 14,
 'Desarrollar sistema de autenticación con Supabase Auth',
 'Desarrollador', 6, 6,
 'Login, JWT, refresh token. Supabase Auth reduce el tiempo de desarrollo'),

('Supabase', 2, 'FASE 2 · Backend Python', 15,
 'Desarrollar API de decisiones compartidas',
 'Desarrollador', 6, 7,
 'Endpoints para publicar, leer y (solo propietario) editar decisiones'),

('Supabase', 2, 'FASE 2 · Backend Python', 16,
 'Desarrollar tablero compartido del equipo',
 'Desarrollador', 7, 7,
 'Vista de feed de decisiones publicadas. Realtime de Supabase opcional'),

-- FASE 3 · Frontend y Seguridad
('Supabase', 3, 'FASE 3 · Frontend y Seguridad', 17,
 'Pantalla de inicio de sesión',
 'Desarrollador', 7, 8,
 'Login corporativo con Supabase Auth'),

('Supabase', 3, 'FASE 3 · Frontend y Seguridad', 18,
 'Adaptar dashboards HTML para múltiples usuarios',
 'Desarrollador', 8, 8,
 'Cada analista ve solo su espacio. Tablero compartido visible para todos'),

('Supabase', 3, 'FASE 3 · Frontend y Seguridad', 19,
 'Pruebas de seguridad: RLS, tokens, acceso no autorizado',
 'Ambos', 8, 9,
 'Participación de TI recomendada. Revisar logs de acceso en Supabase'),

('Supabase', 3, 'FASE 3 · Frontend y Seguridad', 20,
 'Auditoría de trazabilidad: historial de sesiones',
 'Desarrollador', 9, 9,
 'Confirmar que cada acción queda registrada con usuario, fecha y hora'),

-- FASE 4 · Testing y Despliegue
('Supabase', 4, 'FASE 4 · Testing y Despliegue', 21,
 'Pruebas integrales con datos reales SAP',
 'Desarrollador', 9, 10,
 'Ejecutar el sistema completo con el Excel real de SAP'),

('Supabase', 4, 'FASE 4 · Testing y Despliegue', 22,
 'Pruebas de usuario con el equipo de cumplimiento',
 'Ambos', 10, 11,
 'Los 4-5 analistas prueban el sistema en condiciones reales'),

('Supabase', 4, 'FASE 4 · Testing y Despliegue', 23,
 'Correcciones post-pruebas de usuario',
 'Desarrollador', 11, 11,
 'Ajustes de UX, errores detectados, calibración de alertas'),

('Supabase', 4, 'FASE 4 · Testing y Despliegue', 24,
 'Despliegue final — URL activa para todos los usuarios',
 'Ambos', 11, 12,
 'TI confirma acceso desde red corporativa. Supabase activo en producción'),

('Supabase', 4, 'FASE 4 · Testing y Despliegue', 25,
 'Entrega formal y capacitación al equipo',
 'Ambos', 12, 12,
 'Sesión de capacitación. Entrega de manual de usuario básico')

ON CONFLICT (scenario, activity_number) DO NOTHING;


-- ============================================================
-- VERIFICACIÓN FINAL
-- ============================================================
-- Ejecuta esto para confirmar que todo quedó bien:
--
-- SELECT scenario, COUNT(*) as total FROM activities GROUP BY scenario;
-- → Debe mostrar: SQL Server = 25, Supabase = 25
--
-- SELECT * FROM project_config;
-- → Debe mostrar 1 fila con scenario = 'Supabase'
--
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- → Debe mostrar: profiles, project_config, activities, activity_log, user_notes
-- ============================================================
