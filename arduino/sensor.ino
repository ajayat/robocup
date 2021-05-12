#include <HCSR04.h>
#include <Wire.h>

#define THISADRESS 0x10  // from 0x10 to 0x7F (non-reserved) 

#define FRONTSENSORTRIG 2
#define FRONTSENSORECHO 3
#define BACKSENSORTRIG 4
#define BACKSENSORECHO 5

/*
LineSensors
    front left: A0 
    front right: A1 
    rear left: A2 
    rear right: A3 
*/


UltraSonicDistanceSensor frontSensor(FRONTSENSORTRIG,FRONTSENSORECHO);
UltraSonicDistanceSensor backSensor(BACKSENSORTRIG,BACKSENSORECHO);



void setup()
{
    Wire.begin(THISADRESS);
    Wire.onRequest(SendData); //when a request is received, We call SendData

    Serial.begin(9600);

    pinMode(8,OUTPUT);
    digitalWrite(8,HIGH); //pin through which the ultrasonic sensors are powered (5V)
}

void loop()
{   
    PrintSensorsData(); 
    delay(3000);
}


void SendData()
{
    SendInt(frontSensor.measureDistanceCm());
    SendInt(backSensor.measureDistanceCm());

    for(int i = 0; i < 4 ; i++)
    {
        SendInt(analogRead(i));
    }

    Serial.println("On request\n");
}

void SendInt(int i)
{
    Wire.write((byte)highByte(i));
    Wire.write((byte)lowByte(i));
}
