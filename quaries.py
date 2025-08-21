import pymysql
from db import get_connection



# Purchase function
def purchase(player_id, manager_id, amount):
    try:
       conn= get_connection()
       cur = conn.cursor()

       cur.execute("""
            INSERT INTO purchase (player_id, manager_id, amount)
            VALUES (%s, %s, %s)
        """, (player_id, manager_id, amount))

       conn.commit()  # ✅ Commit changes
       print(f"{manager_id} successfully purchased {player_id} for {amount}/-")

    except Exception as e:
        conn.rollback()
        print("Transaction rolled back due to:", e)

    finally:
        cur.close()
        conn.close()


# Cancel purchase function
def cancel_purchase(purchase_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM purchase
            WHERE purchase_id = %s
        """, (purchase_id,))  # ✅ tuple format

        conn.commit()  # ✅ Commit changes
        print(f"Purchase ID {purchase_id} has been cancelled.")

    except Exception as e:
        conn.rollback()
        print("Cancel purchase rolled back due to:", e)

    finally:
        cur.close()
        conn.close()

def select_from_table(table_name: str, filters: dict = None, columns: str = "*"):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = f"SELECT {columns} FROM {table_name}"
            values = []

            if filters:
                conditions = []
                for key, condition in filters.items():
                    # if filter is simple value, treat as "="
                    if not isinstance(condition, dict):
                        conditions.append(f"{key} = %s")
                        values.append(condition)
                    else:
                        # condition is a dict of operator:value
                        for op, val in condition.items():
                            if op not in [">", "<", ">=", "<=", "=", "!=", "LIKE"]:
                                raise ValueError(f"Unsupported operator: {op}")
                            conditions.append(f"{key} {op} %s")
                            values.append(val)

                query += " WHERE " + " AND ".join(conditions)

            cur.execute(query, values)
            result = cur.fetchall()
            return result
    finally:
        conn.close()

def select_by_name(name):
    conn=get_connection()
    try:
        with conn.cursor() as cur:
            query=""" SELECT * FROM players 
            WHERE player_name LIKE %s"""

            cur.execute(query, (f"%{name}%",))
            data=cur.fetchall()
            return data
    finally:
        conn.close() 


        







