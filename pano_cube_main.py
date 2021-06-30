'''
Created on Jun 29, 2021

@author: Duong_Thanh
'''

import os
import numpy as np

import cv2
from PIL import Image

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QResizeEvent
from PyQt5.Qt import QLabel
from PyQt5.QtWidgets import QFileDialog

import threading
from enum import Enum


#add library

######################################################
from support_function import support_func
from numpy.ma.core import get_data
Support_Func = support_func()

from support_function_qt import QT_support_func
Qt_support_Func = QT_support_func() 
######################################################
from support_function_opencv import opencv_process_fun
Image_Process = opencv_process_fun()
######################################################
from qthread_qeventloop import create_thread_qeventloop
Thread_Qeventloop = create_thread_qeventloop()
######################################################


from py360convert_custom import e2c
from py360convert_custom import e2c_custom
from py360convert_custom import c2e_custom


class Ui(QtWidgets.QMainWindow):
    dir = './'
    
    
    class _MODE(Enum):
        Pano_Cube = 0
        Pano_Cube_Pano = 1
    MODE_NAME=["MODE1/", "MODE2/"]
       
    display_image = True;
    is_run_all_now = False;
    stop_run_all = False;
    
    open_folder = "open"
    save_folder = "save"
    mask_file = "mask"
    file_conf = "save_file_path.txt"
    
    
    COLOR_BUTTON_GRAY = "background-color: rgb(200,200,200)"
    # qlabel_input = QLabel()
    # qlabel_output = QLabel()
    
    ratio_out = 0.25
    width = 1000;
    height = 1000;
    blank_image_mat = np.zeros((height,width,3), np.uint8)
    blank_image_ipl = Image.new("RGB", (width, height), color=(100, 100, 100))
    
    do_inpainting = True
    
    # mot so bien khac
    # size_out : size output sau qua trinh pano -> cube
    image = blank_image_ipl.copy() #luu tru anh IPL Image input
    image_output = blank_image_ipl.copy() # -> key qua cuoi cung cua anh cube
    
    size_wid, size_hei = blank_image_ipl.size
    
    # self.width, self.height : size of image
    # ratio_out : he so output based on image.width
    # self.mask -> mask image
    # do_inpainting : cho phep thuc hien inpainting
    
    # self.label_screen_left, self.label_screen_front, self.label_screen_right, self.label_screen_back, self.label_screen_top, 
    # self.label_screen_bottom, self.label_screen_bottom_draw, self.label_screen_bottom_no_inpaint
    
    image_left = blank_image_ipl.copy()
    image_front = blank_image_ipl.copy()
    image_right = blank_image_ipl.copy()
    image_back = blank_image_ipl.copy()
    image_top = blank_image_ipl.copy()
    
    image_bottom = blank_image_ipl.copy()
    image_bottom_draw = blank_image_ipl.copy()
    image_bottom_no_inpaint = blank_image_ipl.copy()
        
    cube_only_show = False;
    
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("pano_cube_inpa.ui", self)
                
        #khoitao
        #################################################
                
        self.qlabel_input = QLabel()
        self.qlabel_output = QLabel()
        
        
        self.run_MODE = self._MODE.Pano_Cube
        self.stackedWidget.setCurrentIndex(self.run_MODE.value)
        self.qlabel_input = self.label_screen_input    
        self.qlabel_output = self.label_screen_output 
                
        #Read conf file
        self.read_conf_file()
        
                
        #thiet lap cac listwidget item click
        self.listWidget_list_files.itemClicked.connect(self.listWidget_click_item)
               
                
        #button click
        self.pushButton_open_browse.clicked.connect(self.open_browse)
        self.pushButton_save_browse.clicked.connect(self.save_browse)
        self.pushButton_mask.clicked.connect(self.get_mask)
        
        #button runn
        self.pushButton_run.clicked.connect(self.process_1_picture)
        self.pushButton_run_all.clicked.connect(self.process_all_picture)
        self.pushButton_stop_run_all.clicked.connect(self.check_stop_run_all)
                               
        # switch mode page
        self.pushButton_mode_change.clicked.connect(self.switch_mode_page)
        
        # action switch page
        self.actioncube_only.triggered.connect(self.set_cube_show_only )
        
        #custom output size
        self.lineEdit_res_out.textChanged.connect(self.set_size_output_manual)
        
        #ratio_output change
        self.verticalScrollBar_ratio_output.valueChanged.connect(self.ratio_output_change)
                       
        self.show()
    
    def do_resize_window(self):
        # thinning small -> 6, thinning big -> 9
        # PANO_CUBE -> 6*3+ 9*2 = 36, 6*2+9*x = 30
        # PANO_CUBE_PANO -> 6 * 1 + 9*" = 24
        if self.run_MODE == self._MODE.Pano_Cube:
            sub_width = 36
            sub_height = 30
            ratio = 3/4
        else :
            sub_width = 0
            sub_height = 0
            ratio = 2/3
            
        w = self.display_layout.width() - 10; #min(self.stackedWidget.width(), self.display_layout.width()) 
        h = self.display_layout.height() - 10 #min(self.stackedWidget.height(), self.display_layout.height())

        if w*ratio < h :
            self.stackedWidget.resize(w, int( (w-sub_width)*ratio+sub_height))
        else :
            self.stackedWidget.resize(int((h-sub_height)*1/ratio+sub_width), h)

        return
    resize_event_ignoge_first_time = True;
    def resizeEvent(self, event):
        if self.resize_event_ignoge_first_time == True :
            self.resize_event_ignoge_first_time = False; 
            return   
        
        self.do_resize()
              
         
    def switch_mode_page(self): #change mode
        Qt_support_Func.GUI_ALARM_(self.pushButton_mode_change, self.COLOR_BUTTON_GRAY)
        
        if self.run_MODE.value == 1 :
            self.run_MODE = self._MODE.Pano_Cube;
            self.label_mode.setText("Pano -> Cube")
            self.pushButton_mode_change.setText("Mode 1")
            
            self.stackedWidget.setCurrentIndex(self.run_MODE.value)
            self.qlabel_input = self.label_screen_input    
            self.qlabel_output = self.label_screen_output  
            
            self.do_resize_window()
            if np.array(self.listWidget_list_files.selectedItems()).size != 0 :
                self.listWidget_click_item(self.listWidget_list_files.currentItem())
            
        else :
            self.run_MODE = self._MODE.Pano_Cube_Pano;
            self.label_mode.setText("Pano -> Cube -> Pano")
            self.pushButton_mode_change.setText("Mode 2")
            
            self.stackedWidget.setCurrentIndex(self.run_MODE.value)
            self.qlabel_input = self.label_pano_input    
            self.qlabel_output = self.label_pano_output 
            
            self.do_resize_window()
            if np.array(self.listWidget_list_files.selectedItems()).size != 0 :
                self.listWidget_click_item(self.listWidget_list_files.currentItem())
                            
            
    def listWidget_click_item(self, item): # click widlist item -> choose object
        if self.is_run_all_now == True:
            return
        
        image_name = item.text()
        link_image = self.textBrowser_path_open.toPlainText() + "/" + image_name;
        
        self.textEdit_name_output.setPlainText(image_name)
        
        #ipl Image
        self.image = Image_Process.Open_Image_ipl_image(link_image) 
        if not self.image is None :      
            self.Display_label(self.image, self.qlabel_input)
            
            #get image size, show label
            self.width, self.height = self.image.size            
            self.label_res_in.setText(str(self.width) + " x " + str(self.height))
                        
            #get size out, show label
            self.size_out = int(self.width*self.ratio_out)
            self.lineEdit_res_out.setText(str(self.size_out))
            
            
            self.cube_only_show = False;
        return
    
    def Display_label(self, image_intput, label_input): #show image tp label
        if self.display_image == True :
            
            Image_Process.Display_pil_image_label(image_intput, label_input)
        Qt_support_Func.delay_ms_loop(10)
        
    def Save_image(self, image_save, name_save): #save image = thread
        x = threading.Thread(target=image_save.save, args=(name_save,))
        x.start()        

        
    def save_image(self, image_save, name_save):
        image_save.save(name_save)      

    def thread_save_image(self, image_save, name_save):
        x = threading.Thread(target=self.save_image, args=(image_save,name_save,))
        x.start()
    
    def ratio_output_change(self): # set ratio size output
        self.ratio_out = float(self.verticalScrollBar_ratio_output.value()/1000);
        # print(self.ratio_out)
        self.label_ratio_out.setText(str(self.ratio_out))        
        
        self.size_out = int(self.width*self.ratio_out)
        self.lineEdit_res_out.setText(str(self.size_out))
    def set_size_output_manual(self): # set output size by input
        self.size_out = int(self.lineEdit_res_out.text())
        return
    # some setting button     
    
    

    def read_conf_file(self):    
        if Support_Func.check_file_exist(self.file_conf) == True :
            f = open(self.file_conf, "r")
            Lines = f.readlines()
            
            count = 0
            for line in Lines:
                count += 1
                get_data = line.strip().split("|")
                if get_data[0] == "open":
                    self.open_folder = get_data[1]
                    Support_Func.check_dir_OK(self.open_folder)
                    if Support_Func.check_dir_OK(self.open_folder):
                        self.set_open_folder()
                        
                        
                if get_data[0] == "save":
                    self.save_folder = get_data[1]
                    if Support_Func.check_dir_OK(self.open_folder):
                        self.set_save_folder()
                        
                        
                if get_data[0] == "mask":
                    self.mask_file = get_data[1]
                    if Support_Func.check_file_exist(self.mask_file):
                        self.set_mask_image()
        # else :
        #     f = open(self.file_conf, "x")
    def save_conf_file(self):
        # return
        f = open(self.file_conf, "w")
        get_data1 = "open|" + self.open_folder + "\n"
        f.writelines(get_data1)
        get_data2 = "save|" + self.save_folder + "\n"
        f.writelines(get_data2)
        get_data3 = "mask|" + self.mask_file + "\n"
        f.writelines(get_data3)
    
    def set_open_folder(self):        
        if self.open_folder != "":
            self.save_conf_file()
            
            self.textBrowser_path_open.setPlainText(self.open_folder)
            
            all_file_list = Support_Func.listfile(self.open_folder) 
            self.listWidget_list_files.clear()      
            for num in range(len(all_file_list)):            
                self.listWidget_list_files.addItem(all_file_list[num]) 
    def open_browse(self):    #load folder images. folder save, mask image 
        Qt_support_Func.GUI_ALARM_(self.pushButton_open_browse, self.COLOR_BUTTON_GRAY)
        
        if Support_Func.check_dir_OK(self.open_folder) == True :
            dirX = self.open_folder
        else :
            dirX = self.dir
        
        self.open_folder = QFileDialog.getExistingDirectory(self, 'Select a directory', dirX)
        
       
        self.set_open_folder()
   
    def set_save_folder(self):
        if self.save_folder != "":
            self.save_conf_file()
            
            self.textBrowser_path_save.setPlainText(self.save_folder)     
    def save_browse(self):    
        Qt_support_Func.GUI_ALARM_(self.pushButton_save_browse, self.COLOR_BUTTON_GRAY)
        
        if Support_Func.check_dir_OK(self.save_folder) == True :
            dirX = self.save_folder
        else :
            dirX = self.dir
        
        
        self.save_folder = QFileDialog.getExistingDirectory(self, 'Select a directory', dirX)
        
        self.set_save_folder()
     
    def set_mask_image(self):   
        if self.mask_file != "":
        # if np.array(fname).size != 0 :
            self.save_conf_file()
            
            self.textBrowser_mask.setPlainText(self.mask_file)
            self.mask = cv2.imread(self.mask_file, cv2.IMREAD_GRAYSCALE)         
    def get_mask(self):
        Qt_support_Func.GUI_ALARM_(self.pushButton_mask, self.COLOR_BUTTON_GRAY)
                 
        fname = QFileDialog.getOpenFileName(None, "Select a file...", self.dir, filter="All files (*)")
        self.mask_file = fname[0]
        
        self.set_mask_image()
         
    def set_cube_show_only(self): #show only cube
        self.cube_only_show = not self.cube_only_show

        if self.cube_only_show == True :
            self.label_screen_bottom_draw.clear()
            self.label_screen_bottom_no_inpaint.clear()
            self.label_screen_input.clear()
            self.label_screen_output.clear()
        else :
            if self.image_bottom_draw is not None:
                self.Display_label(self.image_bottom_draw, self.label_screen_bottom_draw)
            if not self.image_bottom_no_inpaint is None :
                self.Display_label(self.image_bottom_no_inpaint, self.label_screen_bottom_no_inpaint)
            if not self.image is None :
                self.Display_label(self.image, self.qlabel_input)
            if not self.image_output is None :
                self.Display_label(self.image_output, self.qlabel_output)
       
    def process_1_picture(self):  # press run

        # image_output_cube_inpaint_np = np.array(self.image)
        # # image_output_pano_np = c2e_bottom(image_output_cube_inpaint_np, self.height, self.width, 'bilinear')
        #
        # image_output_pano_np = c2e_bottom(image_output_cube_inpaint_np, 3360, 6720, 'bilinear')
        # # return;
        # self.image_output_pano = Image.fromarray(image_output_pano_np.astype(np.uint8))
        # self.Display_label(self.image_output_pano, self.qlabel_output)
        # return
        
        save_path = self.textBrowser_path_save.toPlainText()
        if save_path == "":
            return
        save_open = self.textBrowser_path_open.toPlainText()
        if save_open == "":
            return
        
        
        
        if np.array(self.listWidget_list_files.selectedItems()).size != 0 :
            image_name = self.listWidget_list_files.currentItem().text()
        else :
            return  
        link_image = save_open + "/" + image_name;
        image = np.array(Image.open(link_image))  
        if image.size == 0:
            return
        
        
        Qt_support_Func.GUI_ALARM_(self.pushButton_run, self.COLOR_BUTTON_GRAY)
        
        if self.run_MODE == self._MODE.Pano_Cube :
            self.pano_cube_inpaint_py360(image, image_name, save_path, self.mask)
        if self.run_MODE == self._MODE.Pano_Cube_Pano :
            self.pano_cube_inpaint_cube_py360(image, image_name, save_path, self.mask)
  
    # press run_all
    def check_stop_run_all(self):
        self.stop_run_all = True;
        return    
    def process_all_picture(self):
        
        self.display_image = False
        self.is_run_all_now = True
        
        save_path = self.textBrowser_path_save.toPlainText()
        if save_path == "":
            self.display_image = True
            self.is_run_all_now = False
            return
        save_open = self.textBrowser_path_open.toPlainText()
        if save_open == "":
            self.display_image = True
            self.is_run_all_now = False
            return
        
        Qt_support_Func.GUI_ALARM_(self.pushButton_run_all, self.COLOR_BUTTON_GRAY)
        
        
        for i in range(self.listWidget_list_files.count()) :
            if self.stop_run_all == True :
                self.stop_run_all = False
                self.display_image = True
                self.is_run_all_now = False
                return
            
            # print(i)
            image_name = self.listWidget_list_files.item(i).text()
            link_image = save_open + "/" + image_name;
            
            self.image = Image.open(link_image)
            image = np.array(self.image)  
            if image.size == 0:
                self.display_image = True
                return
            else :
                if i == 0 :                    
                    #get image size, show label
                    self.width, self.height = self.image.size            
                    self.label_res_in.setText(str(self.width) + " x " + str(self.height))
                                
                    #get size out, show label
                    self.size_out = int(self.width*self.ratio_out)
                    self.lineEdit_res_out.setText(str(self.size_out))
                    
                    Qt_support_Func.delay_ms_loop(10)
                    
            self.listWidget_list_files.setCurrentRow(i)     
                      
            if self.run_MODE == self._MODE.Pano_Cube :
                self.pano_cube_inpaint_py360(image, image_name, save_path, self.mask)
            if self.run_MODE == self._MODE.Pano_Cube_Pano :
                self.pano_cube_inpaint_cube_py360(image, image_name, save_path, self.mask)
                
            Qt_support_Func.delay_ms_loop(10)
                    
        
        self.display_image = True
        self.is_run_all_now = False
        return


    def pano_cube_inpaint_py360(self, image, image_name, save_path, mask): # Pano -> Cube
     
        element_size = self.size_out     
        # out = e2c_custom_cube(image, element_size, 'bilinear')
        # out = e2c(image, element_size, 'bilinear')
        
        Thread_Qeventloop.send_task_to_background(e2c, image, element_size, 'bilinear')   
        Thread_Qeventloop.wait_task_end()
        out = Thread_Qeventloop.result
    
        self.image_output = Image.fromarray(out.astype(np.uint8))        
        self.Display_label(self.image_output, self.qlabel_output)
        
                                                
        #left
        image_left_np = out[element_size:element_size+element_size, element_size*0:element_size*0+element_size, :]
        self.image_left = Image.fromarray(image_left_np.astype(np.uint8))
        self.Display_label(self.image_left, self.label_screen_left)
        
        #front
        image_front_np = out[element_size:element_size+element_size, element_size*1:element_size*1+element_size, :]
        self.image_front = Image.fromarray(image_front_np.astype(np.uint8))
        self.Display_label(self.image_front, self.label_screen_front)
        
        #right
        image_right_np = out[element_size:element_size+element_size, element_size*2:element_size*2+element_size, :]
        self.image_right = Image.fromarray(image_right_np.astype(np.uint8))
        self.Display_label(self.image_right, self.label_screen_right)
                
        #back
        image_back_np = out[element_size:element_size+element_size, element_size*3:element_size*3+element_size, :]
        self.image_back = Image.fromarray(image_back_np.astype(np.uint8))
        self.Display_label(self.image_back, self.label_screen_back)
        
        #top
        image_top_np = out[element_size*0:element_size*0+element_size, element_size*1:element_size*1+element_size, :]
        self.image_top = Image.fromarray(image_top_np.astype(np.uint8))
        self.Display_label(self.image_top, self.label_screen_top)
        
        
        
        #bottom inpainting
        image_bottom_np = out[element_size*2:element_size*2+element_size, element_size*1:element_size*1+element_size, :]
        self.image_bottom_no_inpaint = Image.fromarray(image_bottom_np.astype(np.uint8))
        self.Display_label(self.image_bottom_no_inpaint, self.label_screen_bottom_no_inpaint)
        
        if self.do_inpainting == True :
            inpaint_input = Image_Process.pil2cv(self.image_bottom_no_inpaint)
        
            inpaint_draw = inpaint_input.copy()
                
            #imgray = cv2.cvtColor(inpaint_draw, cv2.COLOR_BGR2GRAY)
            # ret, thresh = cv2.threshold(imgray, 60, 255, 0)
                
            size_input = inpaint_draw.shape
        
            mask = cv2.resize(mask, (size_input[1], size_input[0]), interpolation = cv2.INTER_AREA)
            # mask = cv2.resize(mask, (self.size_out, self.size_out), interpolation = cv2.INTER_AREA)
            
            inpaint_output = cv2.inpaint(inpaint_draw, mask, 5, cv2.INPAINT_NS)
                    
            # cv2.imshow("mask", mask)
            
            # Find contours
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # Draw contours
            for i in range(len(contours)):
                color = (255, 0, 0)
                cv2.drawContours(inpaint_draw, contours, i, color, max(1, int(size_input[0]/400)), cv2.LINE_8, hierarchy, 0)
            
            # cv2.imwrite(save_path + "/" + image_name +"_cb_draw.png", inpaint_draw)
            
            
        center_crop = int(size_input[0]/2)
        crop_size = int(size_input[0]/8)
        inpaint_draw_crop_img = inpaint_draw[center_crop-crop_size:center_crop+crop_size, center_crop-crop_size:center_crop+crop_size]
        self.image_bottom_draw = Image_Process.cv2pil(inpaint_draw_crop_img)
        self.Display_label(self.image_bottom_draw, self.label_screen_bottom_draw)
    
                    
                    
        # change to ipl and open
        self.image_bottom = Image_Process.cv2pil(inpaint_output)
        self.Display_label(self.image_bottom, self.label_screen_bottom)
            
        
        #SAVE
        FACE_NAMES = {
            0: 'left',
            1: 'front',
            2: 'right',
            3: 'back',
            4: 'top',
            5: 'bottom',
            6: 'bottom_draw',
            7: 'bottom_no_inpaint',
        }
        
        save_path_end = save_path + "/" + self.MODE_NAME[self.run_MODE.value] + "/"
        if Support_Func.check_dir_OK(save_path_end) < 1:
            os.mkdir(save_path_end)   
        self.Save_image(self.image_left, save_path_end + image_name +"_" +  FACE_NAMES[0] +".png")
        self.Save_image(self.image_front, save_path_end  + image_name +"_" +  FACE_NAMES[1] +".png")
        self.Save_image(self.image_right, save_path_end + image_name +"_" +  FACE_NAMES[2] +".png")
        self.Save_image(self.image_back, save_path_end + image_name +"_" +  FACE_NAMES[3] +".png")
        self.Save_image(self.image_top, save_path_end + image_name +"_" +  FACE_NAMES[4] +".png")  
        self.Save_image(self.image_bottom, save_path_end + image_name +"_" +  FACE_NAMES[5] +".png")
        
            
        inpaint_save = save_path_end + "inpaint/"
        if Support_Func.check_dir_OK(inpaint_save) < 1:
            os.mkdir(inpaint_save)      
        self.Save_image(self.image_bottom, inpaint_save + image_name +"_" +  FACE_NAMES[7] +".png")
        
        no_inpaint_save = save_path_end + "no_inpaint/"
        if Support_Func.check_dir_OK(no_inpaint_save) < 1:
            os.mkdir(no_inpaint_save)
        self.Save_image(self.image_bottom_no_inpaint, no_inpaint_save + image_name +"_" +  FACE_NAMES[7] +".png")
        
        draw_save = save_path_end + "draw/"
        if Support_Func.check_dir_OK(draw_save) < 1:
            os.mkdir(draw_save)
        self.Save_image(self.image_bottom_draw, draw_save + image_name +"_" +  FACE_NAMES[6] +".png")
            
            
    def pano_cube_inpaint_cube_py360(self, image, image_name, save_path, mask): # Pano -> Cube -> Pano

        element_size = self.size_out
        # out = e2c_custom(image, element_size, 'bilinear')
        # out = py360convert.e2c(image, element_size, 'bilinear')
        
        Thread_Qeventloop.send_task_to_background(e2c_custom, image, element_size, 'bilinear')   
        Thread_Qeventloop.wait_task_end()
        out = Thread_Qeventloop.result
        
        

        #output o day cung chinh la bang buttom
        self.image_output = Image.fromarray(out.astype(np.uint8))
        self.Display_label(self.image_output, self.label_pano_bottom)


        self.image_bottom_no_inpaint = Image.fromarray(out.astype(np.uint8))

        if self.do_inpainting == True:
            inpaint_input = Image_Process.pil2cv(self.image_bottom_no_inpaint)

            inpaint_draw = inpaint_input.copy()

            size_input = inpaint_draw.shape

            mask = cv2.resize(mask, (size_input[1], size_input[0]), interpolation=cv2.INTER_AREA)
            # mask = cv2.resize(mask, (self.size_out, self.size_out), interpolation = cv2.INTER_AREA)

            inpaint_output = cv2.inpaint(inpaint_draw, mask, 5, cv2.INPAINT_NS)

            # Find contours
            contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # Draw contours
            for i in range(len(contours)):
                color = (255, 0, 0)
                cv2.drawContours(inpaint_draw, contours, i, color, max(1, int(size_input[0] / 400)), cv2.LINE_8,
                                 hierarchy, 0)

            # cv2.imwrite(save_path + "/" + image_name +"_cb_draw.png", inpaint_draw)

            center_crop = int(size_input[0] / 2)
            crop_size = int(size_input[0] / 8)
            inpaint_draw_crop_img = inpaint_draw[center_crop - crop_size:center_crop + crop_size,
                                    center_crop - crop_size:center_crop + crop_size]
            self.image_bottom_draw = Image_Process.cv2pil(inpaint_draw_crop_img)
            # self.Display_label(self.image_bottom_draw, self.label_screen_bottom_draw)

            # change to ipl and open
            self.image_bottom = Image_Process.cv2pil(inpaint_output)
            self.Display_label(self.image_bottom, self.label_pano_bottom_inpaint)


        bottom_size_w, bottom_size_h = self.image_bottom.size
        fullpic_pano_gray = Image.new("RGB", (bottom_size_w*4, bottom_size_h*3), color=(100, 100, 100))

        fullpic_pano_gray.paste(self.image_bottom, (bottom_size_w * 1, bottom_size_w*2))

        self.ratio_change = 9/10; #75/100
        image_output_cube_inpaint_np = np.array(fullpic_pano_gray)
        # image_output_pano_np = c2e_custom(image_output_cube_inpaint_np, self.height, self.width, self.ratio_change, 'bilinear')

        Thread_Qeventloop.send_task_to_background(c2e_custom, image_output_cube_inpaint_np, self.height, self.width, self.ratio_change, 'bilinear')   
        Thread_Qeventloop.wait_task_end()
        image_output_pano_np = Thread_Qeventloop.result


        #image_output_pano_np chi con ty le 9/10
        self.image_output_pano = Image.fromarray(image_output_pano_np.astype(np.uint8))

        self.image_output = self.image.copy()
        self.image_output.paste(self.image_output_pano, (0, int(self.height*self.ratio_change)))
        self.Display_label(self.image_output, self.qlabel_output)

        # self.image.show()
        # self.image_output.show()

        #SAVE            
        save_path_end = save_path + "/" + self.MODE_NAME[self.run_MODE.value] + "/"
        if Support_Func.check_dir_OK(save_path_end) < 1:
            os.mkdir(save_path_end)    
        self.Save_image(self.image_output, save_path_end + image_name +"_" +  "CUBEFIX" +".png")


app = QtWidgets.QApplication([])
# UI = uic.loadUi("D:/Workspace/QT_creator/pano_cube_inpa/pano_cube_inpa.ui")
# UI.show()

window = Ui()
# window = App("D:/Workspace/QT_creator/pano_cube_inpa/pano_cube_inpa.ui")


app.exec_()
