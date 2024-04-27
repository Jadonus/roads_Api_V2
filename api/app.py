from flask import Flask
import os
from flask import jsonify
import json
import requests
from flask import request
import psycopg2
from database import db
app = Flask(__name__)
pantryid = "f67c5594-75a5-461b-b5d6-5b5b5c27f856"
POSTGRES_URL="postgres://default:ZIDsl9WuH5rS@ep-tiny-sunset-a4k6xpcc-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
POSTGRES_PRISMA_URL="postgres://default:ZIDsl9WuH5rS@ep-tiny-sunset-a4k6xpcc-pooler.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require&pgbouncer=true&connect_timeout=15"
POSTGRES_URL_NO_SSL="postgres://default:ZIDsl9WuH5rS@ep-tiny-sunset-a4k6xpcc-pooler.us-east-1.aws.neon.tech:5432/verceldb"
POSTGRES_URL_NON_POOLING="postgres://default:ZIDsl9WuH5rS@ep-tiny-sunset-a4k6xpcc.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"
POSTGRES_USER="default"
POSTGRES_HOST="ep-tiny-sunset-a4k6xpcc-pooler.us-east-1.aws.neon.tech"
POSTGRES_PASSWORD="ZIDsl9WuH5rS"
POSTGRES_DATABASE="verceldb"






@app.route('/')
def home():
    return 'Hello, World!'
@app.route("/api/newfavorite")
def new_favorite():
    data = request.json
    userid = data.get("userid")
    reference = data.get("reference")
    verse = data.get("verse")
    db.newFavorite(userid=userid, reference=reference, verse=verse)
    return "Success"

@app.route("/api/userdash/")
def user_dash():
    userid = request.args.get("userid")
    roads = db.get_custom_roads_for_user(userid=userid)
    return jsonify(roads)
@app.route('/api/dashboard/')
def dashboard():
    folder_path = os.path.join(os.getcwd(), "roads")
    all_data = []
    final_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Filter JSON files
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                # Process your JSON data here
                all_data.append(data)
    print(all_data)
    """
    api_base_url = f'https://jsonbible.com/search/verses.php?json={{verse_id}}'
    translation_value = "NASB"

            print(verse['chapter'])
            send = {"book": verse['book_name'],  "chapter": str(verse['chapter']),
                                "verse": str(verse['verse_number']), "found": 1,  "version": translation_value.lower()}
            api_url = api_base_url.format(verse_id=json.dumps(send))
            print(api_url)
            api_response = requests.get(api_url)
            print("API Response:", api_response.text)

            api_data = api_response.json()
            print("API Data:", api_data)

            verse_text = api_data.get('verse', 'Verse not found')
            print("Verse Text:", verse_text)

            reference = f"{api_data['book']} {api_data['chapter']}:{api_data['verses']} ({translation_value})"
            final_data =  ({
            'verse': api_data.get('text', 'Verse not found'),
            'reference': reference,
             })  # Append the API data to the list
"""
    # Return the processed data as JSON
    return jsonify(all_data)
@app.route("/api/newcustomroad/", methods=['POST'])
def makeACustomRoad():
    data = request.json
    print(data)
    userid = data.get("userid")
    verses = data.get("verses")
    title = data.get("title")
    new_road_contents = {
        "userid": userid,
        "title":title,
        "verses": verses

    }
    try:

        db.add_custom_road(title=title, verses=verses, userid=userid)
        print(db.get_custom_roads_for_user(userid))
    except:
        print("error getting contetns")
    return "Done"
@app.route("/api/login/", methods=["POSt"])
def login():
    data = request.json
    print(data)
    email = data.get("email")
    password = data.get("password")
    userid = db.login(email=email, password=password)
    return jsonify(userid)

@app.route("/api/createaccount/", methods=["POST"])
def createaccount():
    data = request.json
    print(data)
    userid = data.get("userid")
    email = data.get("email")
    password = data.get("password")
    db.create_account_in_db(userid=userid, email=email, password=password)
    print(db.get_All_In("accounts"))
    return "Account Created"

@app.route("/api/updatetranslation/", methods=["POST"])
def update_translation():
    data = request.json
    userid = data.get("userid")
    translation = data.get("translation")
    db.translation_settings(translation=translation, userid=userid)
    print(db.get_All_In("settings"))
    return "Done"
@app.route("/api/getroad/")
def getroad():
    userid = request.args.get('userid')
    translation_value = db.get_translation_for_user(userid=userid)
    print(translation_value)

    verse = request.args.get('road')
    is_custom = request.args.get('iscustom')
    folder_path = os.path.join(os.getcwd(), "roads")
    final_path = os.path.join(folder_path, f"{verse}" + ".json")
    forloopgoaround = 1
    final_data = []
    description = ""
    title = ""
    api_base_url = f'https://jsonbible.com/search/verses.php?json={{verse_id}}'
    with open(final_path) as road_json:
        data = json.load(road_json)
        for verse in data:

            print(verse)
            print(forloopgoaround)
            print(verse['chapter'])
            send = {"book": verse['book_name'],  "chapter": str(verse['chapter']),
                                "verse": str(verse['verse_number']), "found": 1,  "version": translation_value.lower()}
            api_url = api_base_url.format(verse_id=json.dumps(send))
            print(api_url)
            api_response = requests.get(api_url)
            print("API Response:", api_response.text)

            api_data = api_response.json()
            print("API Data:", api_data)

            verse_text = api_data.get('verse', 'Verse not found')
            print("Verse Text:", verse_text)

            reference = f"{api_data['book']} {api_data['chapter']}:{api_data['verses']} ({translation_value})"
            final_data.append({
            'verse': api_data.get('text', 'Verse not found'),
            'reference': reference,
             })
            print(final_data)
            if forloopgoaround <= 1:
               title = verse["title"]
               description = verse["description"]
            forloopgoaround += 1


    return jsonify({
        "verses": final_data,
        "description":description,
        "title": title

    })
