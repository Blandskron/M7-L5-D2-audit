-- PostgreSQL: el procedimiento registra una auditoría y la función devuelve un conjunto.
CREATE OR REPLACE PROCEDURE sp_register_audit(
    p_user VARCHAR(100), p_action VARCHAR(255), p_severity VARCHAR(10), p_message TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log ("user", action, severity, message, created_at)
    VALUES (p_user, p_action, p_severity, p_message, CURRENT_TIMESTAMP);
END;
$$;

CREATE OR REPLACE FUNCTION sp_audit_summary()
RETURNS TABLE(severity VARCHAR, total BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT al.severity::VARCHAR, COUNT(*)::BIGINT
    FROM audit_log AS al
    GROUP BY al.severity
    ORDER BY COUNT(*) DESC;
END;
$$;

-- Ejemplo para analizar los índices del modelo:
-- EXPLAIN ANALYZE SELECT * FROM audit_log WHERE severity = 'ERROR';
