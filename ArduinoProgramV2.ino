#include <HCSR04.h>
#include <Wire.h>

#define debug

#define THISADRESS 0x10  // from 0x10 to 0x7F (non-reserved) 

#define FRONTSENSORTRIG 2
#define FRONTSENSORECHO 3
#define BACKSENSORTRIG 4
#define BACKSENSORECHO 5

#define LINESENSOR1 A0 //avant gauche
#define LINESENSOR2 A1 //avant droite
#define LINESENSOR3 A2 // arrière gauche
#define LINESENSOR4 A3 // arriere droit


UltraSonicDistanceSensor frontSensor(FRONTSENSORTRIG,FRONTSENSORECHO);
UltraSonicDistanceSensor backSensor(BACKSENSORTRIG,BACKSENSORECHO);


int distanceDevant = 0;
int distanceDerriere = 0;
int lineSensorData[4] = {0};

void setup()
{
    Wire.begin(THISADRESS);
    Wire.onRequest(SendData); //quand une requete est reçue, on appelle SendData
}

void loop()
{
    delay(100);
}

void SendData()
{
    ActualiserDonnees();
    SendInt(distanceDevant);
    SendInt(distanceDerriere);

    for(int i = 0; i < 4 ; i++)
    {
        SendInt(lineSensorData[i]);
    }
}

void SendInt(int i)
{
    byte b[2] = {(byte)highByte(i), (byte)lowByte(i)};
    Wire.write(b, 2);
}

#ifndef debug
void ActualiserDonnees()
{
    distanceDevant = frontSensor.measureDistanceCm();
    distanceDerriere = backSensor.measureDistanceCm();
    
    for (int i = 0; i < 4; i++)
    {
        lineSensorData[i] = analogRead(i);
    }
}
#endif

#ifdef debug
void ActualiserDonnees()
{
    distanceDevant = 100;
    distanceDerriere = 10;
    
    for (int i = 0; i < 4; i++)
    {
        lineSensorData[i] = i*10;
    }
}
#endif