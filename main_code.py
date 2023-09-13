from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import pymongo
from pymongo.mongo_client import MongoClient



app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.find_all('div',{'class':'_3LWZlK _1BLPMq'})[0].text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    commentHead = commentbox.div.div.div.find_all('p',{'class':'_2-N8zT'})[0].text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    custComment = commentbox.div.div.find_all('div',{'class':''})[0].text

                except:
                    custComment = "No customer comment"
                    logging.info(custComment)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info(f"log my final result {reviews}")

            #  Here you have to add the mongodb connect data credentials
            uri = "mongodb+srv://sahildhiman1297:<password>@cluster0.iiheo6v.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            db = client['review_scrap']
            coll_test = db['reviews_scrap_data']
            coll_test.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")