from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import traceback, sys
# import changer
# from changer import *

import urllib.request
import json
import sys
import ctypes
from ctypes import *
import time
import os
import win32api
import cv2
import random
import numpy as np
import time
from time import gmtime, strftime
import fnmatch




SPI_SETDESKWALLPAPER = 0x0014
SPI_GETDESKWALLPAPER = 0x0073
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FOLDER_PATH = "C:/Users/muhamahm/Google Drive/Wallpapers/"
# FOLDER_PATH = "D:/Winter Wallpapers/"
OUTPUT_FOLDER = "D:/TempWall/"
MINUTES = 30
MULTI_ONLY = False
FILTER = ''

def setImageAsBackground(image):
	ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.abspath(image), 0)

def getCurrentBackground():
	ubuf = create_unicode_buffer(200)
	ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 200, ubuf, 0)
	# print(ubuf.value)
	return ubuf.value

def getMonitorInfo():
	monitors = win32api.EnumDisplayMonitors(0)

	# print(len(monitors))
	# print('x\ty\twidth\theight')
	for i in range(len(monitors)):
		output = ''
		for a in range(len(monitors[i][2])):
			output += str(monitors[i][2][a]) + '\t'
		# print(output)
	
	return len(monitors)

def getMonitorCount():
	monitors = win32api.EnumDisplayMonitors(0)
	return len(monitors)

def getImageDimensions(img):	
	# get dimensions of image
	dimensions = img.shape
	
	return img.shape[1], img.shape[0] # width, height

def getRandomImages(count):
	listOfImages = []
	for i in range(count):
		while (True):
			image = random.choice(os.listdir(FOLDER_PATH))
			while (True):	
				if (count != 3):
					if (image.startswith('Multi') == False):
						break
				else:
					if (MULTI_ONLY):
						image = random.choice(fnmatch.filter(os.listdir(FOLDER_PATH), 'Multi*'))
						break
					else:
						break
			if (FILTER != ''):
				image = random.choice(fnmatch.filter(os.listdir(FOLDER_PATH), FILTER + '*'))

			if image not in listOfImages:
				listOfImages.append(image)
				break
	return listOfImages

def returnMultiMonitor(listOfImages):
	for i in range(len(listOfImages)):
		img = cv2.imread(FOLDER_PATH + listOfImages[i])
		x, y = getImageDimensions(img)
		if ((x == 5760) & (y == 1080)):
			return listOfImages[i]
	return ''

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation = inter)
    return resized

def resizeAndCrop(img):
	x,y = getImageDimensions(img)

	if((x == SCREEN_WIDTH) & (y == SCREEN_HEIGHT)):
		return img

	ratio = x/y

	if ((ratio >= 1) & (ratio <= SCREEN_WIDTH/SCREEN_HEIGHT)):
		resized = image_resize(img, width = SCREEN_WIDTH)
		
		cropped = resized
		if (ratio != SCREEN_WIDTH/SCREEN_HEIGHT):
			resized_x, resized_y = getImageDimensions(resized)
			# print(resized_x, resized_y)

			diff = resized_y - SCREEN_HEIGHT
			diff = int(diff/2)

			cropped = resized[diff:diff+SCREEN_HEIGHT, 0:SCREEN_WIDTH]
			cropped_x, cropped_y = getImageDimensions(cropped)
			# print(cropped_x, cropped_y)
	else:
		resized = image_resize(img, height = SCREEN_HEIGHT)
		resized_x, resized_y = getImageDimensions(resized)
		# print(resized_x, resized_y)

		diff = resized_x - SCREEN_WIDTH
		diff = int(diff/2)

		cropped = resized[0:SCREEN_HEIGHT, diff:diff+SCREEN_WIDTH]
		cropped_x, cropped_y = getImageDimensions(cropped)
		# print(cropped_x, cropped_y)
	return cropped

def emptyOutput():
	filelist = [ f for f in os.listdir(OUTPUT_FOLDER) ]
	for f in filelist:
		os.remove(os.path.join(OUTPUT_FOLDER, f))

def changeImage():
	emptyOutput()

	mon_count = getMonitorCount()
	listOfImages = getRandomImages(mon_count)

	if (mon_count == 1):
		multiImage = ''
	else:
		multiImage = returnMultiMonitor(listOfImages)

	if (multiImage != ''):
		# Multi monitor image in multiImage
		
		finalImage = cv2.imread(FOLDER_PATH + multiImage)
		cv2.imwrite(OUTPUT_FOLDER + multiImage, finalImage)

		pathToFinal = OUTPUT_FOLDER + 'out.png'
		cv2.imwrite(pathToFinal, finalImage)

		setImageAsBackground(pathToFinal)

	else:
		# Single images in listOfImages

		loadedImages = []
		for i in range(len(listOfImages)):
			img = cv2.imread(FOLDER_PATH + listOfImages[i])			
			cv2.imwrite(OUTPUT_FOLDER + listOfImages[i], img)

			loadedImages.append(resizeAndCrop(img))

		
		combined = np.concatenate(loadedImages, axis=1)

		pathToFinal = OUTPUT_FOLDER + 'out.png'
		cv2.imwrite(pathToFinal, combined)
		
		setImageAsBackground(pathToFinal)

	output = []
	imagesString = ''
	for i in range(len(listOfImages)):
		 imagesString += '[' + listOfImages[i] + '] '
	
	output.append(' ')
	output.append('======================================================')
	output.append('Photo Changed [' + strftime("%a, %d %b %Y %I:%M:%S %p") + ']')
	output.append('------------------------------------------------------------')
	output.append(imagesString)

	return output
	# print ('Stored in: ' + OUTPUT_FOLDER)


# time.sleep(30) # wait after startup

# while True:	
# 	changeImage()
# 	time.sleep(MINUTES * 60)















class WorkerSignals(QObject):
	'''
	Defines the signals available from a running worker thread.

	Supported signals are:

	finished
		No data

	error
		`tuple` (exctype, value, traceback.format_exc() )

	result
		`object` data returned from processing, anything

	progress
		`int` indicating % progress

	'''
	finished = pyqtSignal()
	error = pyqtSignal(tuple)
	result = pyqtSignal(object)
	progress = pyqtSignal(int)


class Worker(QRunnable):
	'''
	Worker thread

	Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

	:param callback: The function callback to run on this worker thread. Supplied args and 
					 kwargs will be passed through to the runner.
	:type callback: function
	:param args: Arguments to pass to the callback function
	:param kwargs: Keywords to pass to the callback function

	'''

	def __init__(self, fn, *args, **kwargs):
		super(Worker, self).__init__()

		# Store constructor arguments (re-used for processing)
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

		# Add the callback to our kwargs
		self.kwargs['progress_callback'] = self.signals.progress

	@pyqtSlot()
	def run(self):
		'''
		Initialise the runner function with passed args, kwargs.
		'''

		# Retrieve args/kwargs here; and fire processing using them
		try:
			result = self.fn(*self.args, **self.kwargs)
		except:
			traceback.print_exc()
			exctype, value = sys.exc_info()[:2]
			self.signals.error.emit((exctype, value, traceback.format_exc()))
		else:
			self.signals.result.emit(result)  # Return the result of the processing
		finally:
			self.signals.finished.emit()  # Done



class MainWindow(QMainWindow):


	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)

		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER, SCREEN_WIDTH, SCREEN_HEIGHT
		

		self.title = 'Wallpaper Switcher'
		self.width = 500
		self.height = 340
		self.left = (SCREEN_WIDTH/2) - (self.width/2)
		self.top = (SCREEN_HEIGHT/2) - (self.height/2)

		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.labelInput = QLabel('Input Folder:', self)
		self.labelInput.move(10,10)

		self.textboxWallFolder = QLineEdit(self)
		self.textboxWallFolder.move(85, 12)
		self.textboxWallFolder.resize(350,20)
		self.textboxWallFolder.setReadOnly(True)

		self.textboxWallFolder.setText(FOLDER_PATH)



		self.labelOutput = QLabel('Output Folder:', self)
		self.labelOutput.move(10,40)

		self.textboxOutFolder = QLineEdit(self)
		self.textboxOutFolder.move(85, 42)
		self.textboxOutFolder.resize(350,20)
		self.textboxOutFolder.setReadOnly(True)


		self.textboxOutFolder.setText(OUTPUT_FOLDER)


		self.browseWallFolder = QPushButton('Browse', self)
		self.browseWallFolder.move(440,12) 
		self.browseWallFolder.resize(50,20)
		self.browseWallFolder.clicked.connect(self.getWallFolder)

		self.browseOutputFolder = QPushButton('Browse', self)
		self.browseOutputFolder.move(440,42)
		self.browseOutputFolder.resize(50,20)
		self.browseOutputFolder.clicked.connect(self.getOutputFolder)



		self.labelChangeEvery = QLabel('Change every', self)
		self.labelChangeEvery.move(10,70)

		self.textboxMinutes = QLineEdit(self)
		self.textboxMinutes.move(85, 72)
		self.textboxMinutes.resize(40,20)		
		

		self.labelMinutes = QLabel('minutes', self)
		self.labelMinutes.move(130,70)

		self.textboxMinutes.setText(str(MINUTES))

		self.checkboxMulti = QCheckBox("Multi images only", self)
		self.checkboxMulti.move(180,70)


		self.labelFilter = QLabel('Filter', self)
		self.labelFilter.move(310,70)

		self.textboxFilter = QLineEdit(self)
		self.textboxFilter.move(340, 72)
		self.textboxFilter.resize(95,20)
		

		self.buttonUpdate = QPushButton('Update', self)
		self.buttonUpdate.move(440,72) 
		self.buttonUpdate.resize(50,20)


		
		self.buttonStart = QPushButton('Start', self)
		self.buttonStart.move(60,110) 
		self.buttonStart.clicked.connect(self.start_porgram)

		self.buttonPause = QPushButton('Pause', self)
		self.buttonPause.move(200,110) 
		self.buttonPause.clicked.connect(self.pause_program)

		self.buttonChangeWall = QPushButton('Change Walpaper', self)
		self.buttonChangeWall.move(340,110) 
		self.buttonChangeWall.clicked.connect(self.change_now)


		self.labelOutput = QLabel('Logs:', self)
		self.labelOutput.move(20,150)

		self.textboxLog = QTextEdit('', self)
		self.textboxLog.move(20,180)
		self.textboxLog.resize(460,140)
		self.textboxLog.setReadOnly(True)

		# self.show()


		self.count = 0
		self.counter = 0
		self.mins = MINUTES


		self.threadpool = QThreadPool()
		# print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

		self.timer = QTimer()


	def getWallFolder(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		result = QFileDialog.getExistingDirectory(self, "Select Directory")
		if result != '':
			FOLDER_PATH = str(result) + "/"
			self.textboxWallFolder.setText(FOLDER_PATH)

	def getOutputFolder(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		result = QFileDialog.getExistingDirectory(self, "Select Directory")
		if result != '':
			OUTPUT_FOLDER = str(result) + "/"
			self.textboxOutFolder.setText(OUTPUT_FOLDER)

	def on_click_buttonUpdate(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER

		FOLDER_PATH = self.textboxWallFolder.text()
		OUTPUT_FOLDER = self.textboxOutFolder.text()
		MINUTES = int(self.textboxMinutes.text())
		FILTER = self.textboxFilter.text()

		self.mins = MINUTES
		if (self.checkboxMulti.isChecked()):
			MULTI_ONLY = True
		else:
			MULTI_ONLY = False
		# self.textboxLog.append('[Settings Updated]')

	def loadSettings(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER

		self.textboxWallFolder.setText(FOLDER_PATH)
		self.textboxOutFolder.setText(OUTPUT_FOLDER)
		self.textboxMinutes.setText(str(MINUTES))
		self.textboxFilter.setText(FILTER)
		
		self.mins = MINUTES
		self.checkboxMulti.setChecked(MULTI_ONLY)
		self.textboxLog.append('======================================================')
		self.textboxLog.append('[Settings Loaded]')

		self.buttonUpdate.clicked.connect(self.on_click_buttonUpdate)
		self.checkboxMulti.stateChanged.connect(self.on_click_buttonUpdate)	
		self.textboxMinutes.textChanged.connect(self.on_click_buttonUpdate)

	def start_porgram(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		MINUTES = self.mins
		self.count = 0
		
		self.textboxLog.append(' ')
		self.textboxLog.append('======================================================')
		self.textboxLog.append('Program Started [' + strftime("%a, %d %b %Y %I:%M:%S %p") + ']')
		self.textboxLog.append('------------------------------------------------------------')
		self.textboxLog.append('Changing every ' + str(MINUTES) + ' minutes')
		self.textboxLog.append('Photos Folder: ' + FOLDER_PATH)
		self.textboxLog.append('Output Folder: ' + OUTPUT_FOLDER)
		
		output = changeImage()
		
		for i in range(len(output)):
			self.textboxLog.append(output[i])
		
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.recurring_timer)
		self.timer.start()

	def pause_program(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		MINUTES = -1
		self.textboxLog.append('======================================================')
		self.textboxLog.append('[Paused]')
		

	def progress_fn(self, n):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		# print("%d%% done" % n)

	def execute_this_fn(self, progress_callback):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		output = changeImage()
		
		for i in range(len(output)):
			self.textboxLog.append(output[i])

		self.count = 0
		
		return

	def print_output(self, s):
		return

	def thread_complete(self):
		return

	def change_now(self):
		# Pass the function to execute
		worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
		worker.signals.result.connect(self.print_output)
		worker.signals.finished.connect(self.thread_complete)
		worker.signals.progress.connect(self.progress_fn)

		# Execute
		self.threadpool.start(worker)

	def recurring_timer(self):
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER
		
		self.counter += 1 
		self.count += 1
		if (self.count == (MINUTES * 60)):
			output = changeImage()
		
			for i in range(len(output)):
				self.textboxLog.append(output[i])
			
			self.count = 0

	def closeEvent(self, *args, **kwargs):
		super(QMainWindow, self).closeEvent(*args, **kwargs)
		global MULTI_ONLY, FOLDER_PATH, OUTPUT_FOLDER, MINUTES, FILTER

		fileWrite = open("settings.txt","w+")
		fileWrite.write(str(MULTI_ONLY) + ',' + FOLDER_PATH + ',' + OUTPUT_FOLDER + ',' + str(MINUTES) + ',' + FILTER)
		fileWrite.close()

		fileWrite = open("logs.txt","w+")
		fileWrite.write('[' + strftime("%a, %d %b %Y %I:%M:%S %p") + ']\n####################################################################\n' + self.textboxLog.toPlainText() + '\n####################################################################\n')
		fileWrite.close()


# if __name__ == '__main__':
app = QApplication([])
window = MainWindow()

fileRead = open("settings.txt","r")
contents = fileRead.read()

splitContents = contents.split(',')

if splitContents[0] == 'True':
	MULTI_ONLY = True

FOLDER_PATH = splitContents[1]
OUTPUT_FOLDER = splitContents[2]
MINUTES = int(splitContents[3])
FILTER = splitContents[4]

window.loadSettings()

window.show()
window.start_porgram() #-----------------------------------------------Starts on opening-----------------------------------------------

sys.exit(app.exec_())	




