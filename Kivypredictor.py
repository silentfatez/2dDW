
from kivy.app import App
#import widgets:
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.clock import Clock
import glob
import numpy as np
import time
import os

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
os.environ['KIVY_GL_BACKEND']='gl'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    
class Report(App):
    time = NumericProperty(-5)
    temp=NumericProperty(0)
    timestore=[]
    tempstore=[]

    def build(self):
        self.root=root=GridLayout(rows=2,cols=4)
        self.label1=Label(text="Current Time:")
        self.label2=Label(text="Prediction Time:")
        self.label3=Label(text="Temperature Reading:")
        self.label4=Label(text="Prediction Temperature:")   
        self.label_time=Label(text="")
        self.label_predtime=Label(text="")
        self.label_temp=Label(text="")
        self.label_predtemp=Label(text="")
    
        root.add_widget(self.label1)
        root.add_widget(self.label_time)
        root.add_widget(self.label2)
        root.add_widget(self.label_predtime)
        root.add_widget(self.label3)
        root.add_widget(self.label_temp)
        root.add_widget(self.label4)
        root.add_widget(self.label_predtemp)        
        Clock.schedule_interval(self.callback,1)    
        return root
   
         


    def callback(self, instance):
        self.time+=1
        if self.time in [0,2,4,6,8]:
            self.timestore.append(self.time)
            self.tempstore.append(read_temp())
        if self.time==9:
            temparray=np.array(self.tempstore)
            secondsarray=np.array(self.timestore)
            coeffs=np.polynomial.polynomial.polyfit(secondsarray,temparray,1)
            Finaltemp=coeffs[0]+coeffs[1]*16.5
            self.label_predtemp.text=(str(Finaltemp))
            self.label_predtime.text=(str(self.time) + " seconds")

        self.label_temp.text=(str(read_temp()))
        if self.time>-1:
            self.label_time.text=(str(self.time) + " seconds")
            
        else:
            self.label_time.text=(str(0)+" seconds")
        if self.time<0:
            self.label_predtime.text=(str(self.time)+' seconds')
        if self.time==0:
            self.label_predtemp.text=("Put Now")
            self.label_predtime.text=('waiting....')
    
  
if __name__== '__main__':
    Report().run()