#include <Wire.h>

#define SLAVEADDRESS 0x10

int distanceDevant = 0;
int distanceDerriere = 0;

int lineSensors[4] = {0};

void setup()
{
    Wire.begin();
    Serial.begin(9600);
}

void loop()
{
    Wire.requestFrom(SLAVEADDRESS, 6 * sizeof(int)); //requete de 6 entiers

    distanceDevant = ReadInt();
    distanceDerriere = ReadInt();

    for (int i = 0; i< 4; i++)
    {
        lineSensors[i] = ReadInt();
    }


    Serial.println(distanceDevant);
    Serial.println(distanceDerriere);
    for(int i = 0; i < 4; i++)
        Serial.println(lineSensors[i]);

    delay(1000);
}

unsigned int ReadInt()
{
    unsigned int r = 0;
    r = Wire.read();
    r = r << 8;
    r += Wire.read();

    return r;
}
