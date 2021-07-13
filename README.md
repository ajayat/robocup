# Robocup Project
## Informations
The main purpose of this project is to make a robot playing soccer for the Robocup Junior.
To control it we use the [OpenMV H7](https://openmv.io/products/openmv-cam-h7) cam which is a powerful microcontroller equipped of a camera, allowing the ball recognition.
We also use an arduino nano to transmit the data from the sensors to the camera.
***
## OpenMV Programming
The camera code is fully written in Micropython.
To control the motors, the API made is based on the [Arduino API](https://github.com/Makeblock-official/Makeblock-Libraries) for Makeblock [optical encoder motor](https://store.makeblock.com/products/makeblock-steam-education-intermediate-solution-kit?_pos=3&_sid=7f845949e&_ss=r).

## Arduino
The Arduino is here to transmit the data from the sensors to the camera via I2C
