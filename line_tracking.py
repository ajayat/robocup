# Suivi de position de ligne


import sensor, image, time, math , pyb


thresholds = [(0, 60)] #Seuil (min, max)


sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQSIF)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()
ledRouge=pyb.LED(1)


while(True):
    clock.tick()
    img = sensor.snapshot()
    img = img.gaussian(2).scale((0,0,60,10)) #Coupe la partie basse de l'image (l=60, h=10)
    ledRouge.off()
    #Recherche de la ligne et de sa position
    for blob in img.find_blobs(thresholds, pixels_threshold=50, area_threshold=50):
                # recherche des blobs
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        # Note - the blob rotation is unique to 0-180 only.
        print(blob.cx(),' , ', blob.cy(), blob.roundness(),end=' / ')
        ledRouge.on()
    print()

