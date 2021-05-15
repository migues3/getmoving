from flask import Flask, request, Response, render_template
import json
import time
from datetime import datetime

app = Flask(__name__)
numSteps = None
previousNumSteps = None

@app.route("/")
def home():
    return render_template("index.html")

def send_steps():
   global numSteps 
   global previousNumSteps
   while True:
       if numSteps != previousNumSteps:
        json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': numSteps})
        yield "data: {}\n\n".format(json_data)
        previousNumSteps = numSteps

@app.route("/track-steps")
def track_steps():
   global numSteps 
   numSteps = request.args.get("steps")
   
   return Response(send_steps(), mimetype='text/event-stream')  
   #return "Temperature: " + str(request.args.get("temp")) + " Humidity: " + str(request.args.get("humidity"))

@app.route("/track-idle")
def track_idle():
   pass

if __name__ == "__main__":
    app.run()
