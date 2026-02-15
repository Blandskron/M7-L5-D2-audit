CREATE OR REPLACE FUNCTION sp_audit_summary()
RETURNS TABLE(severity VARCHAR, total BIGINT)
AS $$
BEGIN
    RETURN QUERY
    SELECT severity, COUNT(*)
    FROM audit_log
    GROUP BY severity;
END;
$$ LANGUAGE plpgsql;

SELECT severity, COUNT(*)
FROM audit_log
GROUP BY severity;

EXPLAIN ANALYZE
SELECT *
FROM audit_log
WHERE severity = 'ERROR';