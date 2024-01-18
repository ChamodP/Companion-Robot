# import this libraries before running the code

import time
from adafruit_servokit import ServoKit
import multiprocessing
import random
import RPi.GPIO as GPIO
import os
import sys
import datetime
sys.path.append("..")
from PIL import Image
from multiprocessing import Queue
from random import randint

# New imports
import tkinter as tk
from PIL import ImageTk

touch_pin = 12
vibration_pin = 16



# Set up pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)
kit=ServoKit(channels=16)
servo=3

#Declare Servos
servoR = kit.servo[0]#Reference at 0
servoL = kit.servo[2]#Reference at 180
servoB = kit.servo[3]#Reference at 90

frame_count = {'blink':39, 'happy':60, 'sad':47,'dizzy':67,'excited':24,'neutral':61,'happy2':20,'angry':20,'happy3':26,'bootup':90,'blink2':20, 'sleep':112}

emotion = ['angry','sad','excited']

normal = ['neutral','blink2']

def servoDown():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90

currentEmotion='neutral'
currentVibrationEmotion='neutral'
virbrationEmotions=['angry', 'excited', 'sad']

emotion_display = Queue()
emotion_servo = Queue()
emotion_sound = Queue()

def handleDisplay(queue):
    root = tk.Tk()
    root.title("Emotion Display")
    root.geometry(f"{480}x{320}")
    label = tk.Label(root)
    label.pack()

    while True:
        if not queue.empty():
            currentEmotion = queue.get()
        for frame_number in range(frame_count[currentEmotion]):
            # print(currentEmotion)
            # print(frame_number)
            
            image_path = f'/home/pi/Desktop/New/bot/Code/emotions/{currentEmotion}/frame{frame_number}.png'
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = ImageTk.PhotoImage(image)
                label.configure(image=image)
                label.image = image
                root.update_idletasks()



def baserotate(reference,change,timedelay):
    for i in range(reference,reference+change,1):
        servoB.angle = i
        time.sleep(timedelay)
    for j in range(reference+change, reference-change,-1):
        servoB.angle = j
        time.sleep(timedelay)
    for k in range(reference-change, reference,1):
        servoB.angle = k
        time.sleep(timedelay)

def handleMoment(queue):
    while True:
        if not queue.empty():
            currentEmotion = queue.get()
        
        if currentEmotion == 'happy':
            servoDown()
            for i in range(0, 120):
                if i <= 30:
                    servoR.angle = 90 + i  # at 120
                    servoL.angle = 90 - i  # at 60
                    servoB.angle = 90 - i
                elif i > 30 and i <= 90:
                    servoR.angle = 150 - i  # at 60
                    servoL.angle = i + 30  # at 120
                    servoB.angle = i + 30
                elif i > 90:
                    servoR.angle = i - 30  # at 90
                    servoL.angle = 210 - i  # at 90
                    servoB.angle = 210 - i
                time.sleep(0.004)

        elif currentEmotion == 'angry':
            servoDown()
            for i in range(5):
                baserotate(90,randint(0,30),0.01)

        elif currentEmotion == 'excited':
            servoDown()
            for i in range(0,120):
                if i<=30:
                    servoB.angle = 90 - i #at 60
                if (i>30 and i<=90):
                    servoB.angle = i + 30 #at 120
                if(i>90):
                    servoB.angle = 210 - i
                time.sleep(0.01)

        elif currentEmotion == 'sad':
            servoDown()
            for i in range(0,60):
                if i<=15:
                    servoB.angle = 90 - i
                if (i>15 and i<=45):
                    servoB.angle = 60+i
                if(i>45):
                    servoB.angle = 150 - i
                time.sleep(0.09)
                
        elif currentEmotion == 'angry2':
            servoDown()
            for i in range(90):
                servoR.angle = 90-i
                servoL.angle = i+90
                servoB.angle = 90 - randint(-12,12)
                time.sleep(0.02)   

def update_emotion(value):
    global currentEmotion
    currentEmotion = value
    emotion_display.put(value)
    emotion_servo.put(value)
    emotion_sound.put(value)

def sound(queue):
    while True:
        if not queue.empty():
            currentEmotion = queue.get()
        if currentEmotion == 'happy':
            os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/smilling.wav")
        
        if currentEmotion == 'sleep':
            os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/sleep.wav")

        if currentEmotion == 'bootup':
            os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/bootup.wav")

        if currentEmotion == 'angry':
            os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/angry.wav")

        if currentEmotion == 'sad':
            os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/crying.wav")

        
        


#change this one
def bootUp():
    update_emotion('bootup') #need to change
	    

if __name__ == '__main__':

    # Get the current time
    current_time = datetime.datetime.now().time()

    # Define time ranges for morning, evening, and night
    morning_start = datetime.time(6, 0, 0)
    evening_start = datetime.time(18, 0, 0)
    night_start = datetime.time(21, 0, 0)



    back_to_neutral = datetime.datetime.now()
    neutral_to_sleep = datetime.datetime.now() + datetime.timedelta(seconds=30)

    bootUp()
    update_emotion('neutral')
    
    # Compare the current time to the defined time ranges
    if morning_start <= current_time < evening_start:
        os.system("aplay /home/pi/Desktop/New/bot/Code/sounds/morning.wav")
        print("Good morning!")
    elif evening_start <= current_time < night_start:
        print("Good evening!")
    else:
        print("Good night!")

    display_controller = multiprocessing.Process(target=handleDisplay, args=(emotion_display,), name='display_controller')
    handle_moment_functions = multiprocessing.Process(target=handleMoment, args=(emotion_servo,), name='handle_moment_functions')
    handle_sounds_functions = multiprocessing.Process(target=sound, args=(emotion_sound,), name='handle_sounds_functions')
    randomVibrationEmotion = virbrationEmotions[random.randint(0,2)]
    
    display_controller.start()
    handle_moment_functions.start()
    handle_sounds_functions.start()
    

    while True:
        current_time = datetime.datetime.now()
        if (current_time > back_to_neutral) and currentEmotion != 'neutral' and currentEmotion != 'sleep':
            update_emotion('neutral')
            randomVibrationEmotion = virbrationEmotions[random.randint(0,2)]
            neutral_to_sleep = current_time + datetime.timedelta(seconds=30)
        else:
            if(current_time > neutral_to_sleep and currentEmotion == 'neutral'):
                update_emotion('sleep')
                
            elif (GPIO.input(touch_pin) == GPIO.HIGH):
                if currentEmotion != 'happy':
                    update_emotion('happy')
                    back_to_neutral = current_time + datetime.timedelta(seconds=5)

            elif GPIO.input(vibration_pin) == 1:
                if currentEmotion != randomVibrationEmotion:
                    currentEmotion = randomVibrationEmotion
                    update_emotion(currentEmotion)
                    back_to_neutral = current_time + datetime.timedelta(seconds=5)