CREATE OR REPLACE FUNCTION sp_audit_summary()
RETURNS TABLE(severity VARCHAR, total BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT al.severity, COUNT(*)
    FROM audit_log AS al
    GROUP BY al.severity;
END;
$$;

SELECT severity, COUNT(*)
FROM audit_log
GROUP BY severity;

EXPLAIN ANALYZE
SELECT *
FROM audit_log
WHERE severity = 'ERROR';
