import sqlite3

class Database:
    def __init__(self, path: str = "specforge.db"):
        self.path = path
        self.conn = sqlite3.connect(path)
        self._migrate()

    def _migrate(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schema_version (version INT)")
        row = c.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
        v = row[0] if row else 0
        migrations = {1: self._v1, 2: self._v2, 3: self._v3}
        for nv in range(v + 1, max(migrations) + 1):
            migrations[nv]()
            if v == 0:
                c.execute("INSERT INTO schema_version VALUES (?)", (nv,))
            else:
                c.execute("UPDATE schema_version SET version = ?", (nv,))
        self.conn.commit()

    def _v1(self):
        self.conn.execute("""
            CREATE TABLE requirements (
                id TEXT PRIMARY KEY, text TEXT, version INT, created_at INT
            )""")

    def _v2(self):
        self.conn.execute("""
            CREATE TABLE spec_nodes (
                id TEXT PRIMARY KEY, req_id TEXT, content_hash TEXT, content TEXT
            )""")

    def _v3(self):
        self.conn.execute("""
            CREATE TABLE test_results (
                test_id TEXT, spec_version INT, status TEXT, ts INT,
                PRIMARY KEY (test_id, spec_version)
            )""")

    def save_req(self, rid, text, version=1):
        import time
        self.conn.execute(
            "INSERT OR REPLACE INTO requirements VALUES (?,?,?,?)",
            (rid, text, version, int(time.time())))
        self.conn.commit()

    def save_test_result(self, tid, spec_v, status):
        import time
        self.conn.execute(
            "INSERT OR REPLACE INTO test_results VALUES (?,?,?,?)",
            (tid, spec_v, status, int(time.time())))
        self.conn.commit()
