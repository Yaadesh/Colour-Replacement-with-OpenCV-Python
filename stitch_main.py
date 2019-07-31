from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
#from PyQt5.QtCore import QThread
from PyQt5.QtGui import *

import gc

from pynput import keyboard
from pynput.keyboard import Key


#from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSlider
import cv2 
import numpy as np
import threading

hsv_replace = np.uint8([[[177,146,57]]])

mask_for_shirt = np.array([0,0,0],np.uint8)
hsv_replace = np.uint8([[[100,100,100 ]]])
hsv_image = np.uint8([[[0,0,0 ]]])
hsv_point_original = np.uint8([[[0,0,224]]])
hue_val_for_original =0
final_img=''
mouseX = 0
mouseY = 0
mouseX_src =0
mouseY_src=0
saturation_slider_v = 0
value_slider_v =0
result_with_shirt =''

source_img =''
target_img = ''

filenames = ''

height = 0
weight = 0
mouse_pressed_mask = False
mouse_pressed_final= False
default_location = ""

fill_color = 255
ctrl_pressed = False

color_diff_val=-999
color_diff_sat=-999
color_diff_hue = -999

'''
class KeyboardListener (threading.Thread):

		def qt_loop(self): 

			try:
				with keyboard.Listener(
	        			on_press=self.on_press_ctrl,
	        			on_release=self.on_release_ctrl) as listener:
					listener.start()
			except:
				pass


	   

		def __init__(self, threadID, name):
			threading.Thread.__init__(self)
			self.threadID = threadID
			self.name = name


		def run(self):
			 print("Starting " + self.name)
			 self.qt_loop()

		def on_press_ctrl(self,key):
			if key== Key.ctrl:
			    global ctrl_pressed
			    ctrl_pressed = True

		def on_release_ctrl(self,key):
			if key== Key.ctrl:

				global ctrl_pressed
				ctrl_pressed = False

'''

## TO VIEW MASK

def viewMask(image):
		
		#print("in view mask")
		cv2.namedWindow('Mask', cv2.WINDOW_NORMAL)
		cv2.imshow('Mask', image)
		cv2.setMouseCallback('Mask',get_point_mask)	


## HOVER OVER MASK TO GET COLOR IN EACH POINT

def get_point_mask(event,x,y,flags,param):
		global mouse_pressed_mask,fill_color,width,height,ctrl_pressed

		if ((x < (width - 200)) and (y < (height - 200))):

				temp =  mask_for_shirt[y-100:y+100,x-100:x+100]

				#temp_blow_up = cv2.resize(mask_for_shirt,(200, 200), interpolation = cv2.INTER_CUBIC)
				if ctrl_pressed:
					print("ctrl pressed")	
					cv2.namedWindow('Blown',cv2.WINDOW_NORMAL)
					try:
						cv2.imshow('Blown',temp)
						#cv2.waitKey(0)
						#cv2.waitKey(50)
						#cv2.destroyWindow('Blown')
					except Exception:
						pass
				else:
					print("ctrl false")
					cv2.destroyWindow('Blown')
				
		if event == cv2.EVENT_RBUTTONUP :
			
			fill_color = 0 if fill_color == 255 else 255 

		if event == cv2.EVENT_LBUTTONDOWN:
			print("lbutton")
			mouse_pressed_mask = True

		if event == cv2.EVENT_LBUTTONUP:
			mouse_pressed_mask = False

		if mouse_pressed_mask:

				
			
			cv2.circle(mask_for_shirt,(x,y),80,fill_color,-1) #fill_color = 255 by default
			cv2.imshow('Mask',mask_for_shirt)
	    

## HOVER OVER ORIGINAL IMAGE ( the one with the model) TO GET THE COLOR IN EACH POINT

def get_point_original(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDOWN:
		#print(x,y)
		global mouseX,mouseY
		mouseX,mouseY = x,y

## HOVER OVER SOURCE IMAGE ( the one with just the apparel) TO GET THE COLOR IN EACH POINT

def get_point_source(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDOWN:
		global hsv_replace
		temp_image = cv2.imread(source_img)
		#print(temp_image[y,x])
		hsv_replace = cv2.cvtColor(np.uint8([[temp_image[y,x]]]),cv2.COLOR_BGR2HSV)
		a = hsv_replace[0][0]
		print(a)
		print(list([int(a[0]/180*360),int(a[1]/255*100),int(a[2]/255*100)]))

## SATURATION SLIDER HANDLER FOR MASK

def value_change_saturation(val):
	global saturation_slider_v
	saturation_slider_v = val
	low_range = np.array([hue_val_for_original-2,saturation_slider_v,value_slider_v],np.uint8)
	high_range = np.array([hue_val_for_original+2, 255, 255],np.uint8)
	global mask_for_shirt
	mask_for_shirt = cv2.inRange(hsv_image, low_range, high_range)
	cv2.imshow('Mask', mask_for_shirt)
	cv2.setMouseCallback('Mask',get_point_mask)

## VALUE SLIDER FOR MASK

def value_change_val(val):
	global value_slider_v
	value_slider_v = val

	low_range = np.array([hue_val_for_original-2,saturation_slider_v,value_slider_v],np.uint8)
	high_range = np.array([hue_val_for_original+2, 255, 255],np.uint8)
	global mask_for_shirt
	mask_for_shirt = cv2.inRange(hsv_image, low_range, high_range)
	cv2.imshow('Mask', mask_for_shirt)

	
## VIEW ORIGINAL IMAGE (the one with the model)

def viewOriginal(image):
	cv2.namedWindow('Original', cv2.WINDOW_NORMAL)
	cv2.imshow('Original', image)
	cv2.setMouseCallback('Original',get_point_original)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

## DEBUGGING MODULE FOR TESTING THE TARGET IMAGE(original image)

def testing(event,x,y,flags,param):
	#global image
	global hsv_image
	a = hsv_image[y,x]
	print("raw")
	print(a)
	print("converted")
	print(list([int(a[0]/180*360),int(a[1]/255*100),int(a[2]/255*100)]))

## DEBUGGING MODULE FOR TESTING THE FINAL IMAGE

def final_testing(event,x,y,flags,param):
	global final_img
	a = final_img[y,x]
	a=cv2.cvtColor(np.uint8([[final_img[y,x]]]),cv2.COLOR_BGR2HSV)
	a=a[0][0]

	print(type(a[0]))
	print("converted_hsv")
	print(a)
	print("converted_general")
	print(list([int(a[0]/180*360),int(a[1]/255*100),int(a[2]/255*100)]))



## HUE SLIDER FOR FINAL IMAGE FOR MINOR ADJUSTMENTS
 
def hue_final_change_val(val):
	global color_diff_hue
	color_diff_hue = val #- color_diff_hue
	print(color_diff_hue)
	final_image_changes('hue')

## SATURATION SLIDER FOR FINAL IMAGE FOR MINOR ADJUSTMENTS

def sat_final_change_val(val):
	global color_diff_sat
	color_diff_sat= val #- color_diff_sat
	print(color_diff_sat)
	final_image_changes('sat')

## VALUE SLIDER FOR FINAL IMAGE FOR MINOR ADJUSTMENTS

def value_final_change_val(val):
	global color_diff_val
	color_diff_val = val #- color_diff_val
	print(color_diff_val)
	final_image_changes('val')



## EDIT MASK with SLIDERS

def edit_final(event,x,y,flags,param):
	global final_img
	global fill_color
	global mask_for_shirt
	global mouse_pressed_final
	print(mouse_pressed_final)

	if event == cv2.EVENT_LBUTTONUP:
		#print("in left button up")
		mouse_pressed_final = False

	if event == cv2.EVENT_LBUTTONDOWN:
		#print("lbutton")
		mouse_pressed_final = True


	if mouse_pressed_final:
		#print(mouse_pressed_final)
		global mask_for_shirt
		pass
		temp_image = hsv_image
		temp_image = cv2.circle(temp_image,(x,y),40,[[[400,400,400]]],-1) #fill_color = 255 by default 
		temp_image_mask = cv2.inRange(temp_image,[[[]]])
		temp_image_mask = cv2.bitwise_not(temp_image)
		temp_image=cv2.bitwise_and(hsv_image,hsv_image,mask = temp_image_mask)
		viewOriginal(temp_image)
	    


## EDIT FINAL IMAGE for minor adjustments

def final_image_changes(val_to_be_changed):


	global result_with_shirt ,mask_for_shirt , final_img

	global color_diff_hue,color_diff_sat,color_diff_val
	cv2.destroyAllWindows()
	mask_for_background = cv2.bitwise_not(mask_for_shirt)
	result_with_background = cv2.bitwise_and(hsv_image,hsv_image,mask = mask_for_background)
	#result_with_shirt = cv2.bitwise_and(hsv_image,hsv_image,mask = mask_for_shirt)

    
	if val_to_be_changed == 'hue':
		print("hue chnaged")

		result_with_shirt = result_with_shirt.astype(int)
		result_with_shirt[:,:,0]+= color_diff_hue
		h,s,v = cv2.split(result_with_shirt)


		h = np.clip(h,0,179)
		result_with_shirt= cv2.merge([h,s,v])

		result_with_shirt= result_with_shirt.astype(np.uint8)

		'''
		result_with_shirt = cv2.bitwise_and(result_with_shirt,result_with_shirt,mask = mask_for_shirt)
		#print(result_with_shirt)
		result_with_shirt_bgr = cv2.cvtColor(result_with_shirt,cv2.COLOR_HSV2BGR)
		result_with_background_bgr = cv2.cvtColor(result_with_background,cv2.COLOR_HSV2BGR)


		final_img = result_with_shirt_bgr +result_with_background_bgr
		cv2.namedWindow('Final', cv2.WINDOW_NORMAL)
		cv2.imshow('Final', final_img)
		print("final_handler")
		cv2.setMouseCallback('Final',final_testing)
		#cv2.setMouseCallback('Final',edit_final)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		'''

	if val_to_be_changed == 'sat':
	
		print("sat changed")
		#color_diff_sat = actual_value
		result_with_shirt = result_with_shirt.astype(int)
		result_with_shirt[:,:,1]+= color_diff_sat
		h,s,v = cv2.split(result_with_shirt)


		s = np.clip(s,0,254)
		result_with_shirt= cv2.merge([h,s,v])
		result_with_shirt= result_with_shirt.astype(np.uint8)	
		result_with_shirt= cv2.merge([h,s,v])

		result_with_shirt= result_with_shirt.astype(np.uint8)

		'''
		result_with_shirt = cv2.bitwise_and(result_with_shirt,result_with_shirt,mask = mask_for_shirt)
		#print(result_with_shirt)
		result_with_shirt_bgr = cv2.cvtColor(result_with_shirt,cv2.COLOR_HSV2BGR)
		result_with_background_bgr = cv2.cvtColor(result_with_background,cv2.COLOR_HSV2BGR)


		final_img = result_with_shirt_bgr +result_with_background_bgr
		cv2.namedWindow('Final', cv2.WINDOW_NORMAL)
		cv2.imshow('Final', final_img)
		print("final_handler")
		cv2.setMouseCallback('Final',final_testing)
		#cv2.setMouseCallback('Final',edit_final)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		'''
	



	if val_to_be_changed == 'val':
		print("val changed")
		#color_diff_val = actual_value
		result_with_shirt = result_with_shirt.astype(int)
		result_with_shirt[:,:,2]+= color_diff_val
		h,s,v = cv2.split(result_with_shirt)


		v = np.clip(v,0,254)
		result_with_shirt= cv2.merge([h,s,v])


		result_with_shirt= result_with_shirt.astype(np.uint8)


	result_with_shirt = cv2.bitwise_and(result_with_shirt,result_with_shirt,mask = mask_for_shirt)
	#print(result_with_shirt)
	result_with_shirt_bgr = cv2.cvtColor(result_with_shirt,cv2.COLOR_HSV2BGR)
	result_with_background_bgr = cv2.cvtColor(result_with_background,cv2.COLOR_HSV2BGR)


	final_img = result_with_shirt_bgr +result_with_background_bgr
	cv2.namedWindow('Final', cv2.WINDOW_NORMAL)
	cv2.imshow('Final', final_img)
	print("final_handler")
	cv2.setMouseCallback('Final',final_testing)
	#cv2.setMouseCallback('Final',edit_final)
	####cv2.waitKey(0)
	####cv2.destroyAllWindows()


## DISPLAY FINAL IMAGE 

def final_image_handler():

	global result_with_shirt,color_diff_val,color_diff_sat,mask_for_shirt,color_diff_hue
	try:


		cv2.destroyAllWindows()
		mask_for_background = cv2.bitwise_not(mask_for_shirt)
		result_with_background = cv2.bitwise_and(hsv_image,hsv_image,mask = mask_for_background)
		result_with_shirt = cv2.bitwise_and(hsv_image,hsv_image,mask = mask_for_shirt)

		print("hsv replace")
		a = hsv_replace[0][0]
		print(list([int(a[0]/180*360),int(a[1]/255*100),int(a[2]/255*100)]))
		print(a)
		print("hsv original color")
		a = hsv_point_original[0][0]
		print(list([int(a[0]/180*360),int(a[1]/255*100),int(a[2]/255*100)]))
	    
		if color_diff_hue==-999:
			color_diff_hue = int(hsv_replace[:,:,0][0]) - int(hsv_point_original[:,:,0][0])
			#color_diff_hue = temp.astype(int)

		print("====HUE===")
		print("hsv_replace:",hsv_replace[:,:,0][0])
		print("hsv_point_original:",hsv_point_original[:,:,0][0])
		print("hsv_replace-hsv_point_original")
		print("color_diff_hue:",color_diff_hue)

		result_with_shirt = result_with_shirt.astype(int)
		result_with_shirt[:,:,0]+= color_diff_hue
		

		if color_diff_sat==-999:
			color_diff_sat = int(hsv_replace[:,:,1][0]) - int(hsv_point_original[:,:,1][0])
			#color_diff_sat = temp.astype(int)

		print("====SAT===")
		print("hsv_replace:",hsv_replace[:,:,1][0])
		print("hsv_point_original:",hsv_point_original[:,:,1][0])
		print("hsv_replace-hsv_point_original")
		print("color_diff_sat:",color_diff_sat)

		#result_with_shirt[:,:,1]%=255
		
		if color_diff_val==-999:
		#result_with_shirt[:,:,1]%=255
			color_diff_val = int(hsv_replace[:,:,2][0]) - int(hsv_point_original[:,:,2][0])
			#color_diff_val = temp.astype(int)

		print("====VAL===")
		print("hsv_replace:",hsv_replace[:,:,2][0])
		print("hsv_point_original:",hsv_point_original[:,:,2][0])
		print("hsv_replace-hsv_point_original")
		print("color_diff_val:",color_diff_val)
		print(type(color_diff_val))


		result_with_shirt[:,:,2]+=color_diff_val
		result_with_shirt[:,:,1]+= color_diff_sat
		
		#result_with_shirt = np.absolute(result_with_shirt)

		h,s,v = cv2.split(result_with_shirt)



		h = np.clip(h,0,179)
		s = np.clip(s,0,254)
		v = np.clip(v,0,254)


		result_with_shirt= cv2.merge([h,s,v])
		
		
		result_with_shirt= result_with_shirt.astype(np.uint8)
		

		result_with_shirt = cv2.bitwise_and(result_with_shirt,result_with_shirt,mask = mask_for_shirt)
		#print(result_with_shirt)
		result_with_shirt_bgr = cv2.cvtColor(result_with_shirt,cv2.COLOR_HSV2BGR)
		result_with_background_bgr = cv2.cvtColor(result_with_background,cv2.COLOR_HSV2BGR)

		global final_img
		color_diff_sat = 0
		color_diff_val = 0
		color_diff_hue = 0

		final_img = result_with_shirt_bgr +result_with_background_bgr
		cv2.namedWindow('Final', cv2.WINDOW_NORMAL)
		cv2.imshow('Final', final_img)
		print("final_handler")
		cv2.setMouseCallback('Final',final_testing)
		#cv2.setMouseCallback('Final',edit_final)
		####cv2.waitKey(0)
		####cv2.destroyAllWindows()

	except Exception:
		color_diff_val = -999
		color_diff_sat = -999
		color_diff_hue = -999
		result_with_shirt = ''
		print("Trying again....")
		final_image_handler()


## DISPLAY SOURCE IMAGE (the one with just the apparel)


def source_image_handler():
	global source_img
	cv2.namedWindow('Source', cv2.WINDOW_NORMAL)
	dlg = QFileDialog()
	dlg.setFileMode(QFileDialog.AnyFile)

	if dlg.exec_():
	      filenames = dlg.selectedFiles()
	
	source_img = filenames[0]

	cv2.imshow('Source', cv2.imread(source_img))
	cv2.setMouseCallback('Source',get_point_source)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

## TARGET IMAGE HANDLER to select the pixels for mask
	
def target_image_handler():	
		global hsv_image
		global hsv_point_original
		global hue_val_for_original
		global image,height,width
		global target_img
		dlg = QFileDialog()
		dlg.setFileMode(QFileDialog.AnyFile)

		if dlg.exec_():
		      filenames = dlg.selectedFiles()
	
		target_img = filenames[0]

		image = cv2.imread(target_img)
		height,width  = image.shape[:2]
		

		hsv_image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
		'''
		cv2.namedWindow('testing',cv2.WINDOW_NORMAL)	
		cv2.imshow('testing',cv2.cvtColor(hsv_image,cv2.COLOR_HSV2BGR))
		cv2.setMouseCallback('testing',testing)
		cv2.waitKey(0)
		'''
		viewOriginal(image)
		
		hsv_point_original = cv2.cvtColor(np.uint8([[image[mouseY,mouseX]]]),cv2.COLOR_BGR2HSV)

		hue_val_for_original = hsv_point_original[:,:,0]

		#print(hue_val_for_original)

		low_range = np.array([hue_val_for_original-2,saturation_slider_v,value_slider_v],np.uint8)
		high_range = np.array([hue_val_for_original+2, 255, 255],np.uint8)
		global mask_for_shirt
		mask_for_shirt = cv2.inRange(hsv_image, low_range, high_range)
		
		#print(mask_for_shirt)
		viewMask(mask_for_shirt)

## SAVE THE FINAL IMAGE TO DISK

def write_final_handler():
	 global default_location,final_img
	 temp=''
	 if final_img == temp:
	 	label_loc.setText('Please view the image before saving !!')
	 	label_loc.show()
	 else:

		 save_dialog = QFileDialog().getSaveFileName()[0]

		 cv2.imwrite( save_dialog,final_img )
		 #cv2.imwrite( default_location+"mask_final_img.jpg",mask_for_shirt )
		 label_loc.setText("Successfully written to location as "+save_dialog)
		 label_loc.show()

## MANUALLY ADD THE MASK ALREADY OBTAINED

def manual_mask_handler():
	global filenames,mask_for_shirt
	print("mask shape ")
	print(mask_for_shirt.shape)
	dlg = QFileDialog()
	dlg.setFileMode(QFileDialog.AnyFile)

	if dlg.exec_():
	      filenames = dlg.selectedFiles()
	
	mask_file = filenames[0]

	mask_manual_image = cv2.imread(mask_file)
	mask_for_shirt_temp = cv2.cvtColor(mask_manual_image, cv2.COLOR_BGR2GRAY)
	ret,thresh1 = cv2.threshold(mask_for_shirt_temp,250,255,cv2.THRESH_BINARY)
	print(thresh1.shape)
	#mask_for_shirt = cv2.bitwise_or(mask_for_shirt, thresh1)
	mask_for_shirt = thresh1
	viewMask(mask_for_shirt)


app = QApplication([])


window = QWidget()
main_layout = QVBoxLayout()

show_source = QPushButton("Show Source Image")
show_source.clicked.connect(source_image_handler)
show_source.show()

show_target = QPushButton("Show Target Image")
show_target.clicked.connect(target_image_handler)
show_target.show()


label_hue = QLabel()
label_hue.setText("Saturation")


hue_slider = QSlider(Qt.Horizontal)
hue_slider.setFocusPolicy(Qt.StrongFocus)
hue_slider.setTickInterval(10)
hue_slider.setSingleStep(1)

hue_slider.setMinimum(0)
hue_slider.setMaximum(255)
hue_slider.valueChanged[int].connect(value_change_saturation)

label_val = QLabel()
label_val.setText("Value/Lightness")

val_slider = QSlider(Qt.Horizontal)
val_slider.setFocusPolicy(Qt.StrongFocus)
val_slider.setTickInterval(10)
val_slider.setSingleStep(1)

val_slider.setMinimum(0)
val_slider.setMaximum(255)
val_slider.valueChanged[int].connect(value_change_val)

manual_mask = QPushButton("Manual mask")
manual_mask.clicked.connect(manual_mask_handler)
manual_mask.show()


display_final = QPushButton("Display edit")
display_final.clicked.connect(final_image_handler)
display_final.show()

write_final = QPushButton("Save Final")
write_final.clicked.connect(write_final_handler)
write_final.show()

label_hue_final = QLabel()
label_hue_final.setText("Hue Final")
#SAT SLIDER DINAL
hue_final_slider = QSlider(Qt.Horizontal)
hue_final_slider.setFocusPolicy(Qt.StrongFocus)
hue_final_slider.setTickInterval(10)
hue_final_slider.setSingleStep(1)

hue_final_slider.setMinimum(-180)
hue_final_slider.setMaximum(180)
hue_final_slider.valueChanged[int].connect(hue_final_change_val)


label_sat_final = QLabel()
label_sat_final.setText("Saturation")
#SAT SLIDER DINAL
sat_final_slider = QSlider(Qt.Horizontal)
sat_final_slider.setFocusPolicy(Qt.StrongFocus)
sat_final_slider.setTickInterval(10)
sat_final_slider.setSingleStep(1)

sat_final_slider.setMinimum(-255)
sat_final_slider.setMaximum(255)
sat_final_slider.valueChanged[int].connect(sat_final_change_val)

label_val_final = QLabel()
label_val_final.setText("Value/Lightness final")
#VALUE FIMAL SLIDER
val_final_slider = QSlider(Qt.Horizontal)
val_final_slider.setFocusPolicy(Qt.StrongFocus)
val_final_slider.setTickInterval(10)
val_final_slider.setSingleStep(1)

val_final_slider.setMinimum(-255)
val_final_slider.setMaximum(255)
val_final_slider.valueChanged[int].connect(value_final_change_val)

label_loc = QLabel()
label_loc.hide()


main_layout.addWidget(show_source)
main_layout.addWidget(show_target)
main_layout.addWidget(label_hue)

main_layout.addWidget(hue_slider)
main_layout.addWidget(label_val)

main_layout.addWidget(val_slider)
main_layout.addWidget(manual_mask)
main_layout.addWidget(display_final)
main_layout.addWidget(write_final)
main_layout.addWidget(label_loc)
main_layout.addWidget(label_hue_final)
main_layout.addWidget(hue_final_slider)
main_layout.addWidget(label_sat_final)
main_layout.addWidget(sat_final_slider)
main_layout.addWidget(label_val_final)
main_layout.addWidget(val_final_slider)

def line_edit_handler_hue():
	print(line_edit_hue.text())
	#hue_change(int(line_edit_hue.text()))
	global color_diff_hue 
	color_diff_hue= int(line_edit_hue.text())
	final_image_changes('hue')

def line_edit_handler_sat():
	print(line_edit_sat.text())
	global color_diff_sat
	color_diff_sat= int(line_edit_sat.text())
	final_image_changes('sat')
	#sat_change(int(line_edit_sat.text()))

def line_edit_handler_val():
	print(line_edit_val.text())
	global color_diff_val 
	color_diff_val= int(line_edit_val.text())
	final_image_changes('val')
	#val_change(int(line_edit_val.text()))

line_edit_hue = QLineEdit()
line_edit_hue_button = QPushButton('Hue')
line_edit_hue_button.clicked.connect(line_edit_handler_hue)
main_layout.addWidget(line_edit_hue)
main_layout.addWidget(line_edit_hue_button)

line_edit_sat = QLineEdit()
line_edit_sat_button = QPushButton('Sat')
line_edit_sat_button.clicked.connect(line_edit_handler_sat)
main_layout.addWidget(line_edit_sat)
main_layout.addWidget(line_edit_sat_button)

line_edit_val = QLineEdit()
line_edit_val_button = QPushButton('Val')
line_edit_val_button.clicked.connect(line_edit_handler_val)
main_layout.addWidget(line_edit_val)
main_layout.addWidget(line_edit_val_button)

window.setLayout(main_layout)
window.show()

'''
print("before key listener")
thread = KeyboardListener(1,"keyboard_listener")
thread.start()
print("after listener")

'''
app.exec_()
