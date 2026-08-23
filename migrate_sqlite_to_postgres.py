import os, sqlite3
import psycopg
from psycopg.rows import dict_row
from app import init_db, DB_FILE

URL=os.environ.get('DATABASE_URL','').strip()
if not URL:
    raise SystemExit('Set DATABASE_URL first.')

sqlite=sqlite3.connect(DB_FILE); sqlite.row_factory=sqlite3.Row
pg=psycopg.connect(URL, row_factory=dict_row)

def rows(table):
    return [dict(r) for r in sqlite.execute(f'SELECT * FROM {table}').fetchall()]

# Create schema using the app itself.
pg.close()
old=os.environ.get('DATABASE_URL')
# app was imported before URL check, so reconnect directly with same schema DDL.
pg=psycopg.connect(URL, row_factory=dict_row)
with pg.cursor() as c:
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(id BIGSERIAL PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL DEFAULT 'Employee',status TEXT NOT NULL DEFAULT 'Active',can_view_devices INTEGER DEFAULT 1,can_add_devices INTEGER DEFAULT 1,can_edit_devices INTEGER DEFAULT 1,can_delete_devices INTEGER DEFAULT 0,can_view_profit INTEGER DEFAULT 0,can_manage_users INTEGER DEFAULT 0,can_manage_settings INTEGER DEFAULT 0,can_manage_backup INTEGER DEFAULT 0,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS devices(id BIGSERIAL PRIMARY KEY,date TEXT NOT NULL,invoice_no TEXT,merchant TEXT,device_name TEXT NOT NULL,model TEXT,imei TEXT,tax_status TEXT DEFAULT 'معفي',purchase_aed DOUBLE PRECISION DEFAULT 0,purchase_egp DOUBLE PRECISION DEFAULT 0,uae_expenses DOUBLE PRECISION DEFAULT 0,traveler DOUBLE PRECISION DEFAULT 0,receiving DOUBLE PRECISION DEFAULT 0,sale_price DOUBLE PRECISION DEFAULT 0,profit DOUBLE PRECISION DEFAULT 0,loss DOUBLE PRECISION DEFAULT 0,status TEXT DEFAULT 'Available',created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS merchants(id BIGSERIAL PRIMARY KEY,name TEXT UNIQUE NOT NULL);
    CREATE TABLE IF NOT EXISTS device_names(id BIGSERIAL PRIMARY KEY,name TEXT UNIQUE NOT NULL);
    CREATE TABLE IF NOT EXISTS activity_log(id BIGSERIAL PRIMARY KEY,username TEXT,action TEXT NOT NULL,details TEXT,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS notifications(id BIGSERIAL PRIMARY KEY,message TEXT NOT NULL,kind TEXT DEFAULT 'info',is_read INTEGER DEFAULT 0,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    """)
pg.commit()

tables=['users','devices','merchants','device_names','activity_log','notifications','settings']
for table in tables:
    data=rows(table)
    if not data: continue
    cols=list(data[0].keys())
    placeholders=','.join(['%s']*len(cols))
    sql=f'INSERT INTO {table} ({",".join(cols)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
    with pg.cursor() as c:
        for r in data:
            c.execute(sql,[r[k] for k in cols])
    pg.commit()

# Restore sequences after preserving IDs.
for table in ['users','devices','merchants','device_names','activity_log','notifications']:
    with pg.cursor() as c:
        c.execute(f"SELECT setval(pg_get_serial_sequence('{table}','id'), COALESCE((SELECT MAX(id) FROM {table}), 1), true)")
pg.commit(); pg.close(); sqlite.close()
print('Migration completed.')
