from row.row import Row
from dotenv import load_dotenv
import os
import oracledb # import oracle library and explicitly set client as thick mode is required
oracledb.init_oracle_client(lib_dir="/Users/dekockjt/oracle/instantclient_23_26")

load_dotenv()

def connect_db() -> oracledb.Connection:
    user = os.environ['ORA_USER']
    pswd = os.environ['ORA_PASS']
    port = os.environ['ORA_PORT']
    host = os.environ['ORA_HOST']
    name = os.environ['ORA_NAME']
    dsn = f'{host}:{port}/{name}'
    return oracledb.connect(user=user, password=pswd, dsn=dsn)

def query(query: str, binds: dict | None = None, batch_size = 15_000) -> list[Row]:
    try:
        with connect_db() as conn:
            with conn.cursor() as cur:
                cur.arraysize = batch_size
                cur.prefetchrows = batch_size + 1
                cur.execute(query, binds or {})
                if cur.description is None: 
                    return []
                columns = [col[0].lower() for col in cur.description]
                cur.rowfactory = lambda *args: dict(zip(columns, args))
                return cur.fetchall()
    except oracledb.DatabaseError as err:
        raise Exception(f'oracle DB error: {err}') from err
    except Exception as err:
        raise Exception(f'unexpected error occurred: {err}') from err