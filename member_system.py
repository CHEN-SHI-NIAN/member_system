from flask import *
import pymongo
from pymongo.mongo_client import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

uri = "your mongoDB url"

# Create a new client and connect to the server
client = MongoClient(uri)

db =  client.member_system #選擇資料庫
collection = db.users #選擇user集合

app = Flask(
    __name__,
    static_folder = "public",
    static_url_path="/"
)

app.secret_key="1234"

#處理路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/member")
def member():
    if "nickname" in session:
        user = collection.find_one({"nickname": session["nickname"]})
        return render_template("member.html", nickname=user["nickname"])
    else:
        return  redirect("/")

#/error?msg=錯誤訊息
@app.route("/error")
def error():
    message= request.args.get("msg","發生錯誤，請聯繫客服")
    return render_template("error.html",message=message)

@app.route("/signup", methods = ["POST"])
def singup():
    #前端接收資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    #檢查是否有相同email
    result = collection.find_one({
        "email":email
    })
    if result!= None:
        return redirect("/error?msg=信箱已被使用")
    # 將密碼加密後存入資料庫
    hashed_password = generate_password_hash(password)  # 改進：使用密碼加密
    collection.insert_one({
        "nickname": nickname,
        "email": email,
        "password": hashed_password  # 改進：儲存加密後的密碼
    })
    return redirect("/")


@app.route("/signin", methods=["POST"])
def signin():
    email = request.form["email"]
    password = request.form["password"]

    result = collection.find_one({"email": email})
    if result is None or not check_password_hash(result["password"], password):
        return redirect("/error?msg=帳號或密碼輸入錯誤")

    session["nickname"] = result["nickname"]
    return redirect("/member")

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json
    address = data['address']
    abi = data['abi']
    functions = [item['name'] for item in abi if item['type'] == 'function']
    
    result = f"Processed address: {address} with functions: {functions}"

    return jsonify({'result': result, 'functions': functions})

@app.route("/signout")
def singout():
    session.pop("nickname", None)
    return redirect("/")

@app.route("/comingsoon")
def comingsoon():
    return render_template("comingsoon.html")


app.run(port=3000)
