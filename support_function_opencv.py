'''
Created on Jun 29, 2021

@author: Duong_Thanh
'''



import cv2
from PIL import Image
import numpy as np
# from PyQt5.Qt import QImage, QTimer, QEventLoop, QLabel
# from PyQt5.QtGui import QPixmap, QResizeEvent
 
from PyQt5.QtGui import QPixmap, QImage

class opencv_process_fun():    
    def cv2pil(self, image):
        new_image = image.copy()
        if new_image.ndim == 2: 
            pass
        elif new_image.shape[2] == 3: 
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4: 
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image
    
    def pil2cv(self, image):
        new_image = np.array(image, dtype=np.uint8)
        if new_image.ndim == 2:  
            pass
        elif new_image.shape[2] == 3: 
            new_image = new_image[:, :, ::-1]
        elif new_image.shape[2] == 4: 
            new_image = new_image[:, :, [2, 1, 0, 3]]
        return new_image    
    

    def Open_Image_Mat(self, link_image): #Open and display for MAT
        self.image = cv2.imread(link_image, cv2.IMREAD_COLOR)
        # if not image is None :            
        #     #resize de ra kich thuoc chuan
        #     resize = True
        #     if(resize == True) :            
        #         image_size = image.shape
        #         size_hei = image_size[0]
        #         size_wid = image_size[1]
        #
        #         #convert gia tri
        #         if((size_hei*self.label_screen.width())>(size_wid*self.label_screen.height())) :
        #             y = self.label_screen.height();
        #             x = y*size_wid/size_hei;
        #         else :
        #             x = self.label_screen.width();
        #             y = x*size_hei/size_wid;
        #
        #         image = cv2.resize(image, (int(x), int(y)), interpolation = cv2.INTER_AREA);
        #
        #         self.Display_mat_label(image, self.label_screen)
    def Display_mat_label(self, image, label):         
        image_size = image.shape
        size_hei = image_size[0]
        size_wid = image_size[1]
                        
        #convert gia tri
        if((size_hei*label.width())>(size_wid*label.height())) :
            y = label.height();
            x = y*size_wid/size_hei;
        else :
            x = label.width();
            y = x*size_hei/size_wid;
                        
        image = cv2.resize(image, (int(x), int(y)), interpolation = cv2.INTER_AREA);
            
        if image.strides[1]==1:
            qimage = QImage(image.data,image.shape[1], image.shape[0] , image.strides[0] , 
                        QImage.Format_Indexed8).rgbSwapped() 
        elif image.strides[1]==3:
            qimage = QImage(image.data,image.shape[1], image.shape[0] , image.strides[0] , 
                        QImage.Format_RGB888).rgbSwapped()
        elif image.strides[1]==4:
            qimage = QImage(image.data,image.shape[1], image.shape[0] , image.strides[0] , 
                        QImage.Format_RGB32).rgbSwapped() 
                        
        pitmap = QPixmap.fromImage(qimage)
        label.setPixmap(pitmap)
    
    
    # Open and display for IPL image
    def Open_Image_ipl_image(self, link_image):
        image = Image.open(link_image) 
        return image
    def Display_pil_image_label(self, image_intput, label_input):
        size_wid, size_hei = image_intput.size
        #convert gia tri
        if((size_hei*label_input.width())>(size_wid*label_input.height())) :
            y = label_input.height();
            x = y*size_wid/size_hei;
        else :
            x = label_input.width();
            y = x*size_hei/size_wid;
        
        image = image_intput.resize((int(x), int(y))) 
                
        if image.mode == "RGB":
            r, g, b = image.split()
            image = Image.merge("RGB", (b, g, r))
        elif  image.mode == "RGBA":
            r, g, b, a = image.split()
            image = Image.merge("RGBA", (b, g, r, a))
        elif image.mode == "L":
            image = image.convert("RGBA")
        # Bild in RGBA konvertieren, falls nicht bereits passiert
        im2 = image.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, image.size[0], image.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        label_input.setPixmap(pixmap)

