from flask import Flask, render_template, redirect
from Flask_PyMongo import PyMongo
import scrape_mars

# Create an instance of Flask
app = Flask(__name__)

# Use PyMongo to establish Mongo connection
# create a connection to Mongo DB: 
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


# Route to render index.html template using data from Mongo
#day 3 activity 8
@app.route("/")
def home():

    # Find one record of data from the mongo database
    destination_data = mongo.db.find_one()

    # Return template and data
    return render_template("index.html", mars=destination_data)


# Route that will trigger the scrape function
@app.route("/scrape")
def scrape():
    
    mars = mongo.db.mars

    # Run the scrape function (call the function from the scrape_mars.py)
    mars_data = scrape_mars.scrape_info()

    # Update the Mongo database using update and upsert=True
    mars.update_one({}, {"$set": mars_data}, upsert=True)

    # Redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)