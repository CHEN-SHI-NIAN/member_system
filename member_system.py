from flask import *
import pymongo
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://root:tiger871031@mycluster.mhzco2q.mongodb.net/?retryWrites=true&w=majority&appName=myCluster"

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

@app.route("/singup", methods = ["POST"])
def singup():
    #前端接收資料
    nickname = request.form["nickname"]
    email = request.form["email"]
    password = request.form["password"]
    #檢查是否有相同email
    result=collection.find_one({
        "email":email
    })
    if result!= None:
        return redirect("/error?msg=信箱已被使用")
    #放資料
    collection.insert_one({
        "nickname":nickname,
        "email" :email,
        "password" : password
    })
    return redirect("/")


@app.route("/singin",methods=["POST"])
def singin():
    email = request.form["email"]
    password = request.form["password"]
    collection = db.users
    result = collection.find_one({
        "$and":[
            {"email" :email},
            {"password":password}
        ]
    })
    if result == None:
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    session["nickname"] = result["nickname"]
    return redirect("/member")

@app.route('/process_data', methods=['POST'])
def process_data():
    data = request.json
    address = data['address']
    abi = data['abi']
    result = f"Processed address: {address} with ABI: {abi}"

    return jsonify({'result': result})

@app.route("/singout")
def singout():
    del session["nickname"]
    return redirect("/")

app.run(port=3000)
