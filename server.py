from flask import Flask, request, Response, render_template
import json
import time
from datetime import datetime

app = Flask(__name__)
numSteps = 0
previousNumSteps = -1

@app.route("/")
def home():
    return render_template("index.html")

def send_data():
   global numSteps 
   global previousNumSteps
   while True:
       if numSteps != previousNumSteps:
        json_data = json.dumps({'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'value': numSteps})
        yield f"data: {json_data}\n\n"
        previousNumSteps = numSteps

@app.route("/track-steps")
def track():
   global numSteps 
   numSteps = request.args.get("steps")

   if numSteps is None:
       numSteps = 0 
   
   return Response(send_data(), mimetype='text/event-stream')  
   #return "Temperature: " + str(request.args.get("temp")) + " Humidity: " + str(request.args.get("humidity"))

if __name__ == "__main__":
    app.run()