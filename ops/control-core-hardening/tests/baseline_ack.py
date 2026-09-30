def ack_external_sync(target, outcome, observed_external_version=None, error=None):
    """Acknowledge a leased item after connector-side verification."""
    if outcome not in ("succeeded", "retry", "conflict", "quarantined"):
        raise ValueError("invalid external-sync outcome")
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pending_external_sync WHERE id=%s OR stable_id=%s FOR UPDATE", (target, target))
            row = cur.fetchone()
            if not row:
                raise KeyError("external sync item not found")
            if row["status"] in ("succeeded", "conflict", "quarantined"):
                conn.commit()
                return row
            if row["status"] != "in_progress":
                raise RuntimeError("external sync item is not leased")
            final_outcome = outcome
            completed = None
            available = row["available_at"]
            if outcome == "retry":
                if int(row["attempts"]) >= int(row["max_attempts"]):
                    final_outcome = "quarantined"
                    completed = now()
                else:
                    available = now() + dt.timedelta(seconds=min(900, 2 ** min(int(row["attempts"]), 9)))
                    final_outcome = "pending"
            else:
                completed = now()
            cur.execute(
                """UPDATE pending_external_sync
                   SET status=%s,available_at=%s,observed_external_version=%s,locked_by=NULL,lease_until=NULL,
                       completed_at=%s,last_error=%s WHERE id=%s""",
                (final_outcome, available, observed_external_version, completed, error, row["id"]),
            )
            audit(cur, "external_sync.ack", row["entity_type"], row["entity_id"],
                  {"outcome": final_outcome, "attempt": row["attempts"],
                   "expected_external_version": row.get("expected_external_version"),
                   "observed_external_version": observed_external_version, "error": error},
                  f"audit:external-sync:ack:{row['stable_id']}:{row['attempts']}:{final_outcome}")
            cur.execute("SELECT * FROM pending_external_sync WHERE id=%s", (row["id"],))
            updated = cur.fetchone()
        conn.commit()
        return updated
    finally:
        conn.close()

def endpoint(parts,a):
    return ack_external_sync(parts[2],a["outcome"],a.get("observed_external_version"),a.get("error"))
