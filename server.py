from flask import Flask, request, Response, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import time
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Steps(db.Model):
   date = db.Column(db.Date, primary_key = True)
   count = db.Column(db.Integer, nullable = False)

   def __repr__(self):
        return "Steps: {} {}".format(self.date, self.count)

class Idle(db.Model):
   date = db.Column(db.Date, primary_key = True)
   count = db.Column(db.Integer, nullable = False)   

   def __repr__(self):
        return "Idle: {} {}".format(self.date, self.count)


numSteps = 0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/my-steps")
def my_steps():
   stepsPerDay = {}

   lastSeven = Steps.query.order_by(Steps.date).limit(7).all()
   
   for step in lastSeven:
      stepsPerDay[str(step.date)] = step.count
   
   return render_template("my-steps.html", steps = stepsPerDay)

@app.route("/my-idle")
def my_idle():
   idlePerDay = {}

   lastSeven = Idle.query.order_by(Idle.date).limit(7).all()

   for idle in lastSeven:
      idlePerDay[str(idle.date)] = idle.count

   return render_template("my-idle.html", idle = idlePerDay)

def send_steps():
   global numSteps 

   while True:
      day = datetime.now().date()
      stepsFromDB = Steps.query.filter_by(date = day).first()

      # If step count != the step count in database we must update database
      if numSteps != stepsFromDB.count and numSteps is not None:

         stepsFromDB.count = numSteps
         db.session.commit()

         # Send steps to main chart
         json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': numSteps})
         yield "data: {}\n\n".format(json_data)

@app.route("/track-steps")
def track_steps():
   global numSteps

   day = datetime.now().date()
   stepsFromDB = Steps.query.filter_by(date = day).first()

   # Check if already in database
   if stepsFromDB is None:
      db.session.add(Steps(date=day, count=0))
      db.session.commit()

   numSteps = request.args.get("steps")
   if numSteps is not None:
      numSteps = int(numSteps)
   
   return Response(send_steps(), mimetype='text/event-stream')  

@app.route("/track-idle")
def track_idle():
   idleNum = request.args.get("idleNum")
   print("Idle num = ", idleNum)
   day = datetime.now().date()
   idleFromDB = Idle.query.filter_by(date = day).first()
   print("idlefromdb =", idleFromDB)

   if idleFromDB is None:
      db.session.add(Idle(date=day, count=idleNum))
      db.session.commit()
   else:
      idleFromDB.count = idleNum
      db.session.commit()   

   return idleNum

if __name__ == "__main__":
    app.run()
