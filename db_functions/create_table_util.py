import psycopg

def create_table(conn_str, table_name, columns, primary_key):

    column_defs = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())

    query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
            {column_defs},
            PRIMARY KEY ({primary_key})
            )
            """
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            print(f"table {table_name} made successfully")