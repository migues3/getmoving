#include <SparkTime.h>
#include <HttpClient.h>
#include <SparkFunMMA8452Q.h>
#include <math.h>

#define IDLE_TIME 20000 // Time in ms to delay between prints.
#define BUZZER D3


UDP UDPClient;
SparkTime rtc;
unsigned long currentTime;
String timeStr;

HttpClient http;
// Headers currently need to be set at init, usefulfor API keys etc.
http_header_t headers[] = { 
    //{ "Content-Type", "application/json" },
    //{ "Accept" , "application/json" },
    { "Accept" , "*/*"},
    { NULL, NULL } // NOTE: Always terminate headerswill NULL
};

http_request_t request;
http_response_t response;

bool isIdle = true;
bool trackedIdle = false;
bool isStep = false; 
float previous = 1.0;
float threshold = .15;
float newRead = 0.0;
float score = 0;
unsigned long timer;
int steps = 0;
int idle = 0;

MMA8452Q accel;

void setup() {
    
    Serial.begin(9600);
    rtc.begin(&UDPClient, "north-america.pool.ntp.org");
    rtc.setTimeZone(-1); // gmt offset
    
    pinMode(BUZZER,OUTPUT);
    accel.begin(SCALE_2G, ODR_1); // Set up accel with +/-2g range, and slowest (1Hz) ODR
    delay(2000);
    timer = millis(); // Start time for idle time
    
    timeStr = rtc.monthString(currentTime) + rtc.dayString(currentTime) + rtc.yearString(currentTime);
    
    Serial.println("Counting steps...");
}

void loop() {
    
    if (accel.available()) {
        accel.read();
        newRead = sqrt((accel.cx * accel.cx) + (accel.cy * accel.cy) + (accel.cz * accel.cz));
        score = abs(previous - newRead);

        if (score >= threshold && !isStep) {
            steps++;
            digitalWrite(BUZZER, LOW);
            
            Serial.print("Steps taken: ");
            Serial.println(steps);
            
            // Send number of steps to server in incremenets of 5
            if (steps % 5 == 0) {
                
                // If its a new day, reset steps
                if (timeStr != rtc.monthString(currentTime) + rtc.dayString(currentTime) + rtc.yearString(currentTime)) {
                    steps = steps % 5;
                }
                
                Serial.println("Sending request...");
                request.hostname = "3.80.75.59";
                request.port = 5000;
                request.path = "/track-steps?steps=" + String(steps);
                http.get(request, response, headers);
                Serial.println("Request sent...");
                delay(100);
            }

            if (isIdle == true) {
                isIdle = false;
            }

            isStep = true;
            trackedIdle = false;
            timer = millis();
        }
        else if (score >= threshold && isStep) {
            isStep = false;
        }
        else if (isIdle && millis() - timer > IDLE_TIME) {
            // turn on buzzer
            Serial.println("Idle for too long!");
            
            if (!trackedIdle) {
                
                // if it's a new day, reset idle
                if (timeStr != rtc.monthString(currentTime) + rtc.dayString(currentTime) + rtc.yearString(currentTime)) {
                    idle = 1;
                }
                
                trackedIdle = true;
                idle++;
                
                Serial.println("Sending request for idle...");
                
                request.hostname = "3.80.75.59";
                request.port = 5000;
                request.path = "/track-idle?idleNum=" + String(idle);
                http.get(request, response, headers);
                
                Serial.println("Sent request for idle...");
            }
            
            digitalWrite(BUZZER, HIGH);
        }
        
        delay(100);
		isIdle = true;
		previous = newRead;
    }
}