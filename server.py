from flask import Flask, request, Response, render_template
import json
import time
from datetime import datetime

app = Flask(__name__)
numSteps = None
previousNumSteps = None
stepsPerDay = {}
idlePerDay = {}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/my-steps")
def my_steps():
   if len(stepsPerDay) > 7:
      keys = list(stepsPerDay.keys())
      stepsPerDay.pop(keys[0], None)
   
   return render_template("my-steps.html", steps = stepsPerDay)

@app.route("/my-idle")
def my_idle():
   if len(idlePerDay) > 7:
      keys = list(idlePerDay.keys())
      idlePerDay.pop(keys[0], None)

   return render_template("my-idle.html", idle = idlePerDay)

def send_steps():
   global numSteps 
   global previousNumSteps
   global stepsPerDay

   while True:
       if numSteps != previousNumSteps:

        day = datetime.now().strftime('%Y-%m-%d')
        stepsPerDay[day] = numSteps

        json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': numSteps})
        yield "data: {}\n\n".format(json_data)
        previousNumSteps = numSteps

@app.route("/track-steps")
def track_steps():
   global numSteps 
   numSteps = request.args.get("steps")
   
   return Response(send_steps(), mimetype='text/event-stream')  

@app.route("/track-idle")
def track_idle():
   idleNum = request.args.get("idleNum")
   day = datetime.now().strftime('%Y-%m-%d')

   idlePerDay[day] = idleNum 

   return idleNum

if __name__ == "__main__":
    app.run()
