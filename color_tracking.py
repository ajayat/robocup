import sensor, image, time, math

# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# The below thresholds track in general red/green things. You may wish to tune them...
thresholdOrange = [(53, 83, -4, 33, 44, 76)] #orange color
thresholdRed = [(0, 100, -128, 127, 55, 127)]
thresholdGreen = [(19, 94, -57, -19, -14, 37)] #green color


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

# Only blobs that with more pixels than "pixel_threshold" and more area than "area_threshold" are
# returned by "find_blobs" below. Change "pixels_threshold" and "area_threshold" if you change the
# camera resolution. Don't set "merge=True" because that will merge blobs which we don't want here.

while(True):
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs(thresholdRed, pixels_threshold=200, area_threshold=200):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        print("red x: {}, red y: {}".format(blob.cx(), blob.cy()))
