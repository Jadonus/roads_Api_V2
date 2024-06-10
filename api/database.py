import psycopg2
import json
import bcrypt


POSTGRES_URL="postgres://default:ZIDsl9WuH5rS@ep-tiny-sunset-a4k6xpcc-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
connection = psycopg2.connect(POSTGRES_URL)

class db:
    @staticmethod
    def add_custom_road(verses, title, userid):
        print("Adding custom road ", title)
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS customRoads (
                            id SERIAL PRIMARY KEY,
                            title TEXT,
                            verses JSONB,
                            userid TEXT
                        );
                    """)
                    cursor.execute("""
                        INSERT INTO customRoads (title, verses, userid)
                        VALUES (%s, %s, %s);
                    """, (title, json.dumps(verses), userid))
            return "Custom road added successfully."
        except psycopg2.Error as e:
            return f"Error adding custom road: {e}"
    @staticmethod
    def get_favorites_for_user(userid):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM favorites WHERE userid = {userid}")
    @staticmethod
    def delete_road(userid, road):
        with connection:
            with connection.cursor() as cursor:
                print(road, userid)
                cursor.execute(f"DELETE FROM customroads WHERE title = '{road}' AND userid = '{userid}'")
    @staticmethod
    def get_favs_for_road(userid, road):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM favorites WHERE road='Freedom' AND userid = '{userid}'")
                return cursor.fetchall()
    @staticmethod
    def translation_settings(userid, translation):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        id SERIAL PRIMARY KEY,
                        translation TEXT,
                        userid TEXT UNIQUE
                    );
                """)
                cursor.execute(f"""
                    INSERT INTO settings (userid, translation)
                    VALUES (%s, %s)
                    ON CONFLICT (userid)
                    DO UPDATE SET translation = EXCLUDED.translation;
                """, (userid, translation))


    @staticmethod
    def get_progress_for_road(userid, road):
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT progress FROM roadprogress
                        WHERE userid='{userid}' AND road='{road}';
                    """)
                    return cursor.fetchone()

        except psycopg2.Error as e:
            print(e)

    @staticmethod
    def road_progress_update(userid, progress,road):
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS roadprogress (
                        id SERIAL PRIMARY KEY,
                        progress INTEGER,
                        userid TEXT,
                        road TEXT
                    );
                    """)

                    # Check if the record already exists
                    cursor.execute("""
                        SELECT id FROM roadprogress
                        WHERE userid = %s AND road = %s;
                    """, (userid, road))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        # If record exists, perform UPDATE
                        cursor.execute("""
                            UPDATE roadprogress
                            SET progress = %s
                            WHERE userid = %s AND road = %s;
                        """, (progress, userid, road))
                    else:
                        # If record doesn't exist, perform INSERT
                        cursor.execute("""
                            INSERT INTO roadprogress (progress, userid, road)
                            VALUES (%s, %s, %s);
                        """, (progress, userid, road))
        except psycopg2.Error as e:
            print(e)
        print("done")



    @staticmethod
    def get_translation_for_user(userid):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT translation FROM settings WHERE userid = %s;
                """, (userid,))
                result = cursor.fetchone()
                if result is not None:
                   return result[0]
                else:
                    return "NLT"
    @staticmethod
    def get_custom_roads_for_user(userid):
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                            SELECT *
                            FROM customroads
                            WHERE userid = %s;
                    """, (userid,))
                    columns = [desc[0] for desc in cursor.description]
                    data = cursor.fetchall()
                    print(data)
                    results = []
                    for row in data:
                        results.append(dict(zip(columns, row)))
                    return results
        except psycopg2.Error as e:
            return f"Error retrieving custom roads: {e}"

    @staticmethod
    def get_custom_road(userid, title):
        try:
            with connection:
                with connection.cursor() as cursor:
                    query = "SELECT * FROM customRoads WHERE userid = %s AND title = %s"
                    cursor.execute(query, (userid, title))
                    return cursor.fetchall()
        except psycopg2.Error as e:
            return f"Error retrieving custom roads: {e}"
    @staticmethod
    def get_All_In(db):
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {db};")
                return cursor.fetchall()


    @staticmethod
    def newFavorite(userid, verse, reference, road):
        with connection:
            with connection.cursor() as cursor:

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS favorites (
                        id SERIAL PRIMARY KEY,
                        verse TEXT,
                        reference TEXT,
                        userid TEXT,
                        road TEXT
                    );
                """)
                cursor.execute(f"""
INSERT INTO favorites (verse, reference, userid, road)
VALUES ({verse}, {reference}, {userid}, {road});
                """)


    @staticmethod
    def login(email, password):
        userid = ""

        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT password FROM accounts WHERE email = %s
                    """, (email,))
                    hashed_password = cursor.fetchone()[0]
                    print(hashed_password.encode("utf-8"), password.encode("utf-8"))
                    cursor.execute("""
                        SELECT userid FROM accounts WHERE email = %s
                        """, (email,))
                    userid = cursor.fetchone()[0]
            # Verify the password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return userid
            else:
                return {"error": "Wrong Password"}

        except (psycopg2.Error, IndexError) as e:
            return str(e)


    @staticmethod
    def create_account_in_db(userid, email, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            with connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS accounts (
                            id SERIAL PRIMARY KEY,
                            userid TEXT,
                            email TEXT,
                            password TEXT
                        );
                    """)
                    cursor.execute("""
                        INSERT INTO accounts (userid, email, password)
                        VALUES (%s, %s, %s)
                    """, (userid, email, hashed_password))
            return("Account Created")



        except psycopg2.Error as e:
            return(f"error {e}")
