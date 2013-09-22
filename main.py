#! /usr/bin/env python
import random
import numpy as np
import math
import Image
import ImageQuilting
import time

print "results preview"
time.sleep(2)

box1=(50,50,350,350)
box2=(400,50,700,350)
box3=(750,50,1050,350)

a1=Image.open("apples1.png")
a2=Image.open("apples2.png")
a3=Image.open("apples3.png")
apples=Image.new("RGB",(1150,450))
apples.paste(a1,box1)
apples.paste(a2,box2)
apples.paste(a3,box3)
apples.show()

time.sleep(2)

r1=Image.open("radish1.png")
r2=Image.open("radish2.png")
r3=Image.open("radish3.png")
radishes=Image.new("RGB",(1150,450))
radishes.paste(r1,box1)
radishes.paste(r2,box2)
radishes.paste(r3,box3)

pic1 = "apples.png"
print "apples!"

print("random patching")
apple1 = quilt_random(pic1, (300,300), (60, 60))
time.sleep(3)

print("overlapping patching")
apple2 = quilt_simple(pic1, (300,300), (60, 60), 10)
time.sleep(3)

print("seam patching")
apple3 = quilt_seam(pic1, (300,300), (60, 60), 10)
time.sleep(3)


pic2 = "radishes.png"
print "radishes!"

print("random patching")
radish1 = quilt_random(pic2, (300,300), (50, 50))

print("overlapping patching")
radish2 = quilt_simple(pic2, (300,300), (60, 60), 10)

print("seam patching")
radish3 = quilt_seam(pic2, (300,300), (60, 60), 10)
