from transformers import pipeline
from flask import Flask, render_template, request
from flask_restful import Api ,Resource ,request ,abort 
from http import HTTPStatus
import re

app = Flask(__name__)
api = Api(app)


def is_persian(text: str) -> bool:
    return bool(re.fullmatch(r'[\u0600-\u06FF\s]+', text))


def mapping(result:dict) -> tuple[str,int]:
    if result["label"] == "LABEL_0":
        cat = "ادبیات"
    elif result["label"] == "LABEL_1":
        cat = "سینما"
    elif result["label"] == "LABEL_2":
        cat = "ورزش"
    return cat ,round(result["score"] * 100,2)


model = pipeline("text-classification",model="./Model_Classification",tokenizer="./Model_Classification")


@app.route("/")
def home():
    return render_template("index.html", category=None ,score=None)

@app.route("/submit", methods=["POST"])
def submit():
    user_input = request.form["text"]
    result = model(user_input)[0]  
    cat, score = mapping(result)
    return render_template("index.html", category=cat,score=score)


class Text_api(Resource):
    def get(self ,text=None) -> dict:
        try:
            if is_persian(text):
                result = model(text)[0] 
                cat, score = mapping(result)
                return ({"category": cat,"score": score}), HTTPStatus.OK                                         
            return abort(HTTPStatus.BAD_REQUEST ,Message='یافت نشد!' ,Code=HTTPStatus.BAD_REQUEST )    
        
        except Exception as e:
            return {"error": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

api.add_resource(Text_api ,'/text' ,'/text/<string:text>')


if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1',port=8080)

'mahdi'