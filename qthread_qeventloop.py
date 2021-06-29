'''
Created on Jun 29, 2021

@author: Duong_Thanh
'''


import time
import threading

from PyQt5.Qt import QTimer, QEventLoop
from PyQt5.QtCore import QObject, pyqtSignal 
       
#note : cai nay chi dung dvoi qloop event.
# con neu dung thread bt thi hay dung cac thread khac nhu la threading 
class create_thread_qeventloop(QObject):
    signal_stop_loop = pyqtSignal()    
    loop_for_wait = QEventLoop()
        
    trigger = pyqtSignal()  
    
    result = 0  
    
    # Sample
# def delayxx(a, b, c):
    # time.sleep(1)  
    # print(str(a))
    # time.sleep(1) 
    # print(str(b))
    # time.sleep(1)   
    # print(str(c))   
    # print("quit")

# app = QtWidgets.QApplication([])
# ABC = create_thread_qeventloop()  

# element_size = 1680
# image_open = Image.open("C:/thanh/Workspace/Pycharm/pythonProject_test/pn_cb_python-270621/sample_1/R0010057_20210608203558.JPG")
# image = np.array(image_open) 
# ABC.send_task_to_background(e2c_custom, image, element_size, 'bilinear' )

# ABC.send_task_to_background(delayxx, 4, 6, 19)   

# print("wait task here")
# ABC.wait_task_end()
# print("task finished")
# print(ABC.result)

# app.exec()   
    
    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        
        #connect signal to loop.quit
        self.signal_stop_loop.connect(self.loop_for_wait.quit)
        
            
    def run_task_then_emit(self, task, *args):    
        self.result = task(*args)
        
        self.signal_stop_loop.emit()    
        
    # do run_task_then_emit as background
    def send_task_to_background(self, task, *args): 
        do_task_by_thread = 1
        if  do_task_by_thread == 1:
            x = threading.Thread(target=self.run_task_then_emit, args=(task, *args))
            x.start()
        else :        
            time_one_shot = QTimer()
            time_one_shot.timeout.connect(task(*args))
            time_one_shot.setSingleShot(True)
            time_one_shot.start(0) # do as 0ms later
            
            
    # run task -> emit    
    def run_task_then_emit_no_return(self, task, args=()):    
        self.result = task(args)
        self.signal_stop_loop.emit()
    
    # do run_task_then_emit as background
    def send_task_to_background_no_return(self, task, args=()):   
        do_task_by_thread = 1
        if  do_task_by_thread == 1:
            x = threading.Thread(target=self.run_task_then_emit, args=(task, args))
            x.start()
        else :        
            time_one_shot = QTimer()
            time_one_shot.timeout.connect(task(args))
            time_one_shot.setSingleShot(True)
            time_one_shot.start(0) # do as 0ms later            
         
          
    def wait_task_end(self):
        self.loop_for_wait.exec()

    def connect_and_emit_trigger(self, func):
        test = 1
        # Connect the trigger signal to a slot.
        if test == 0 :
            self.trigger.connect(func)
        else :
            self.trigger.connect(self.handle_trigger)
            
        print(10)
        time.sleep(3)
        # Emit the signal.
        self.trigger.emit()

    def handle_trigger(self):
        # Show that the slot has been called.
        print("trigger signal received")
        
