import psycopg2

from cfg import db_url_object

with psycopg2.connect(db_url_object) as conn:

    def create_tables() -> None:
        create_partners_table()
        create_users_table()

    def create_partners_table() -> None:
        """ Функция, которая сначала удаляет таблицу 'Partners', если она уже есть, а затем создает новую. """

        with conn.cursor() as cursor:
            cursor.execute("""DROP TABLE IF EXISTS Partners;""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Partners(
                    finder_id INTEGER,
                    partner_id INTEGER,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    PRIMARY KEY(finder_id, partner_id)
                    );
                """)
            conn.commit()

    def create_users_table():
        """ Функция, которая создает таблицу 'Users', если её нет. """

        with conn.cursor() as cursor:
            cursor.execute("""DROP TABLE IF EXISTS Users;""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY,
                    fcity INTEGER,
                    fgender INTEGER CHECK(fgender IN(1, 2)),  
                    fage INTEGER,
                    ffamily INTEGER CHECK(ffamily IN(1, 2, 3, 4, 5, 6, 7, 8)),
                    step INTEGER CHECK (step IN(1, 2, 3, 4, 5, 6)),
                    vkoffset INTEGER
                );
                """)
            conn.commit()

    def insert_partners(data):
        """ Функция, добавляющая в таблицу 'Partner'  подошедших по заданным критериям кандидатов. """

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Partners(finder_id, partner_id, first_name, last_name) VALUES(%s, %s, %s, %s);
                """, (data[0], data[1], data[2], data[3]))
            conn.commit()


    def get_user_from_db(finder_id):
        """ Функция, выдающая по запросу пользователя данные об одном случайном кандидате из таблицы 'Partners'. """

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT partner_id, first_name, last_name FROM Partners WHERE finder_id = %s;
                """, (finder_id,))
            return cursor.fetchone()


    def delete_candidate(finder_id, partner_id):
        """ Функция, которая удаляет просмотренных кандидатов из таблицы """

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Partners WHERE partner_id = %s AND finder_id = %s;
                """, (partner_id, finder_id,))
            conn.commit()


    def delete_candidates(finder_id):

        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Partners WHERE finder_id = %s;
                """, (finder_id,))
            conn.commit()




    def insert_user(uid):
        """ Функция, добавляющая в таблицу 'Users' нового пользователя  """

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Users(id, step, vkoffset) VALUES(%s, 1, 0);
                """, (uid,))
            conn.commit()


    def update_user_city(uid, cid):


        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fcity = %s WHERE id = %s;
                """, (cid, uid,))
            conn.commit()


    def update_user_age(uid, age):


        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fage = %s WHERE id = %s;
                """, (age, uid,))
            conn.commit()


    def update_user_gender(uid, gender):



        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET fgender = %s WHERE id = %s;
                """, (gender, uid,))
            conn.commit()


    def update_user_family(uid, family):



        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET ffamily = %s WHERE id = %s;
                """, (family, uid,))
            conn.commit()


    def update_user_position(uid, step):


        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Users SET step = %s WHERE id = %s;
                """, (step, uid,))
            conn.commit()


    def get_user_settings(uid):

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT fcity, fgender, fage, ffamily FROM Users WHERE id = %s;
                """, (uid,))

            return cursor.fetchone()


    def take_position(uid):

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT step FROM Users WHERE id = %s;
                """, (uid,))
            position = cursor.fetchone()
            if position:
                return position[0]
            else:
                insert_user(uid)
                return 1

    def increment_user_offset(user_id, to_add):
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET vkoffset = vkoffset+%s WHERE id = %s RETURNING vkoffset;
                """, (to_add, user_id))
            conn.commit()
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return 0