from flask import Flask
from flask import request
from flask import Response
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def hello():
   def send_data():
       while True:
           json_data = json.dumps(
               {'time': datetime.now().strftime('%Y-%m%d %H:%M:%S'), 'value': request.args.get("temp")}
           yield f"data: {json_data}\n\n"
           time.sleep(1)
   
   return Response(send_data(), mimetype='text/event-stream')  
   #return "Temperature: " + str(request.args.get("temp")) + " Humidity: " + str(request.args.get("humidity"))
