import sqlite3
from typing import List, Optional, Tuple, Any

from config import DATABASE_URL



class SQLiteDB:
    def __init__(self, db_path: str = DATABASE_URL):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def open_connection(self):
        """Открыть соединение с базой данных."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Чтобы возвращать результаты как dict-подобные объекты
            self.cursor = self.conn.cursor()

    def close_connection(self):
        """Закрыть соединение с базой данных."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_data(
        self,
        table: str,
        columns: List[str] = ['*'],
        where_clause: Optional[str] = None,
        where_params: Optional[Tuple[Any, ...]] = None,
    ) -> List[sqlite3.Row]:
        """
        Получить данные из таблицы.

        :param table: имя таблицы
        :param columns: список столбцов или ['*'] для всех
        :param where_clause: строка с условием WHERE без ключевого слова WHERE (например, "id = ? AND status = ?")
        :param where_params: кортеж или список параметров для where_clause (защита от SQL-инъекций)
        :return: список строк (sqlite3.Row)
        """
        if self.conn is None or self.cursor is None:
            raise RuntimeError("Connection is not opened. Call open_connection() first.")

        cols = ", ".join(columns)
        sql = f"SELECT {cols} FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        if where_params:
            self.cursor.execute(sql, where_params)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchall()

    def save_data(
        self,
        table: str,
        data: dict,
        where_clause: Optional[str] = None,
        where_params: Optional[Tuple[Any, ...]] = None,
    ) -> None:
        """
        Вставить новую запись или обновить существующую в таблице.

        :param table: имя таблицы
        :param data: словарь с колонками и их значениями для вставки/обновления
        :param where_clause: условие WHERE для обновления (без ключевого слова WHERE). Если None — будет выполнена вставка (INSERT)
        :param where_params: параметры для where_clause (кортеж)
        """
        if self.conn is None or self.cursor is None:
            raise RuntimeError("Connection is not opened. Call open_connection() first.")

        if where_clause is None:
            # Вставка новой записи
            columns = ", ".join(data.keys())
            placeholders = ", ".join("?" for _ in data)
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            params = tuple(data.values())
            self.cursor.execute(sql, params)
        else:
            # Обновление существующей записи
            set_clause = ", ".join(f"{col} = ?" for col in data.keys())
            sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            params = tuple(data.values()) + (where_params if where_params else ())
            self.cursor.execute(sql, params)

        self.conn.commit()





# # Пример использования:
# try:
#     db.open_connection()

#     # Получить все данные из таблицы users
#     all_users = db.get_data('users')
#     for user in all_users:
#         print(dict(user))

#     # Получить reveal_count и user_status_id из users, где id = 1
#     user = db.get_data('users', columns=['reveal_count', 'user_status_id'], where_clause='id = ?', where_params=[1])
#     print(user)



#     # Вставка новой записи
#     db.save_data(
#         table='users',
#         data={'id': 123, 'reveal_count': 0, 'user_status_id': 1}
#     )

#     # Обновление существующей записи
#     db.save_data(
#         table='users',
#         data={'reveal_count': 0},
#         where_clause='id = ?',
#         where_params=[123]
#     )


# finally:
#     db.close_connection()
