# Robocup project
***
## Informations
The main purpose of this project is to make a robot playing soccer for the robocup junior.
To control it we use the [openmv h7](https://openmv.io/products/openmv-cam-h7) cam which is a powerful microcontroller equipped of a camera, allowing the ball recognition.
We also use an arduino nano to transmit the data from the sensors to the camera.
***
## Openmv programming
The camera code is fully written in micropython.
***
To control the motors, the API made is based on the [arduino API](https://github.com/Makeblock-official/Makeblock-Libraries) for Makeblock [optical encoder motor](https://store.makeblock.com/products/makeblock-steam-education-intermediate-solution-kit?_pos=3&_sid=7f845949e&_ss=r).

## Arduino
The arduino is here to transmit the data from the sensors to the camera via i2c