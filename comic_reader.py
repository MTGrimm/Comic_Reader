# Hidden Browser with selenium to nav webpage with the custom gui
from asyncio import Future
from genericpath import isfile
from multiprocessing.dummy import Pool
import shutil
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor, process
from logging import exception
from tokenize import group
from turtle import forward
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import sys
from PyQt5.QtCore import QUrl, Qt, QSize, QDataStream, QByteArray, QIODevice, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication, QLabel, QPushButton, QGridLayout, QVBoxLayout, QWidget, QLineEdit, QListWidget, QHBoxLayout, QScrollArea, QToolBar, QAction, QProgressDialog
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QKeySequence, QFont, QImage, QPixmap, QGuiApplication
from adblockparser import AdblockRules
from PyQt5.QtWebEngineCore import *
from PyQt5.uic import loadUi
import requests
from multiprocessing import Process, Pool
import time
from bs4 import BeautifulSoup

if __name__ == "__main__":
    abs_path = os.path.dirname(__file__)
    print("owo")
    option = Options()
    option.headless = False
    driver = webdriver.Firefox(options=option, service=Service(abs_path + "\geckodriver.exe"))
    driver.install_addon(r"Python/Comic Reader/adblock.xpi", temporary=True)

    driver.get("https://comiconlinefree.net/")

def last_opened(rel_path):
    with open(abs_path + "/" + rel_path, "r") as file:#
        url = file.read()
        return url  
    
def custom_get(driver, url):
    driver.get(url)
    
def preload2(forward_url, update_image):
    print("made it to preload2")
    soup = BeautifulSoup(requests.get(forward_url).content, "html.parser")
    imgs = soup.find_all("img", {"class" : "lazyload chapter_img"})
    image_links = []
    for img in imgs:
        image_links.append(img.get("data-original"))
        
    for link in image_links:
        image = QImage()
        image.loadFromData(requests.get(link).content)
        image = image.scaled(int(image.width()*1.15), int(image.height()*1.15))
        update_image(QPixmap(image))    
    
def preload(forward_url):
    soup = BeautifulSoup(requests.get(forward_url).content, "html.parser")
    imgs = soup.find_all("img", {"class" : "lazyload chapter_img"})
    image_links = []
    for img in imgs:
        image_links.append(img.get("data-original"))
    
    state = []
    for i, link in enumerate(image_links):
        print("owo")
        qByte = QByteArray()
        stream = QDataStream(qByte, QIODevice.WriteOnly)
        image = QImage()
        image.loadFromData(requests.get(link).content)
        image = image.scaled(int(image.width()*1.15), int(image.height()*1.15))
        stream << image
        state.append((i, qByte))
    return state


def forward(forward_url):
    driver.get(forward_url)
    forward_url = driver.find_element(By.CLASS_NAME, "nav.next").get_attribute("href")
    p = Process(target=preload,args=(forward_url, ))
    p.start()
    p.join()
    
    
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(QPixmap)
    def __init__(self, forward_url, driver):
        super(Worker, self).__init__()
        self.forward_url = forward_url
        self.driver = driver
    
    def run(self):
        print("made it to run")
        self.driver.get(self.forward_url)
        preload2(self.forward_url, self.update_image)
        self.finished.emit()
        
    def update_image(self, pix):
        self.progress.emit(pix)
    
    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        
        self.searchWidget = QWidget()
        self.comicWidget = QWidget()
        self.issueWidget = QWidget()
        
        # Search Bar
        self.search = QLineEdit()
        self.searchEnter = QPushButton("ENTER")
        self.search.setText("ENTER COMIC HERE")
        self.searchEnter.clicked.connect(self.search_comic)

        self.searchWidget.setLayout(QHBoxLayout())
        self.searchWidget.layout().addWidget(self.search)
        self.searchWidget.layout().addWidget(self.searchEnter)

        
        self.mainWidget.setLayout(QVBoxLayout())
        self.mainWidget.layout().addWidget(self.searchWidget)
        self.mainWidget.layout().addWidget(self.comicWidget)
        self.mainWidget.layout().addWidget(self.issueWidget)
        
        self.comicList = QListWidget()
        self.comicList.setAlternatingRowColors(True)
        self.comicEnter = QPushButton("ENTER")
        self.comicEnter.clicked.connect(self.go_to_comic)
        self.comicWidget.setLayout(QHBoxLayout())
        self.comicWidget.layout().addWidget(self.comicList)
        self.comicWidget.layout().addWidget(self.comicEnter)
        
        self.issueList = QListWidget()
        self.issueList.setAlternatingRowColors(True)
        self.issueEnter = QPushButton("ENTER")
        self.issueEnter.clicked.connect(self.go_to_issue)
        self.issueWidget.setLayout(QHBoxLayout())
        self.issueWidget.layout().addWidget(self.issueList)
        self.issueWidget.layout().addWidget(self.issueEnter)
        
        self.preload_data = []

        # Main Window
        self.setMinimumSize(800, 500)
        self.show()
        
    def search_comic(self):
        searchBar = driver.find_element(By.ID, "autocomplete")
        searchBar.send_keys(self.search.text())
        self.get_comics()
        
    def get_comics(self):
        self.comicList.clear()
        try:
            WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "search-result")))
        except TimeoutException as e:
            print(e)
            
        items = driver.find_elements(By.CLASS_NAME, "item")
        for item in items:
            if item.find_element(By.XPATH, "./..").tag_name != "p":
                self.comicList.addItem(item.text)
    
    def go_to_comic(self):
        chosen_name = self.comicList.currentItem().text()
        i = 1
        chosen = driver.find_element(By.XPATH, f"//a[normalize-space()='{chosen_name}']")
        
        url = chosen.get_attribute("href")
        driver.get(url)
        
        self.get_issues()
        
    def get_issues(self):
        self.issueList.clear()
        issue_elements = driver.find_elements(By.CLASS_NAME, "ch-name")
        for issue in issue_elements:
            self.issueList.addItem(issue.text)
        
    def go_to_issue(self):
        chosen_name = self.issueList.currentItem().text()
        chosen = driver.find_element(By.XPATH, f"//a[normalize-space()='{chosen_name}']")
    
        url = chosen.get_attribute("href")
        
        if url[-5:-1] + url[-1] != "/full":
            url = url + "/full"
        driver.get(url)
        
        self.get_images()
        
    def get_images(self):
        images = []
        url = driver.current_url
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        imgs = soup.find_all("img", {"class" : "lazyload chapter_img"})
        for img in imgs:
            images.append(img.get("data-original"))
        
        self.display_comic(images)
        
    def display_comic(self, imageLinks):   
        self.readingList = QWebEngineView()
        self.readingList.setUrl(QUrl(last_opened("lasturl2.txt")))
        
        self.stacked = QStackedWidget()
        
        self.popup = QMainWindow()
        self.popup.setWindowFlag(Qt.FramelessWindowHint)
        self.popup.setMinimumSize(1200, 1800)
        self.navBar = QToolBar("Navigator")
        self.navBar.setIconSize(QSize(0, 0))
        self.navBar.setFixedWidth(0)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
        self.navBar.setFixedHeight(0)

        back = QAction("back", self)
        back.triggered.connect(self.go_back)
        back.setShortcut(QKeySequence("Alt+Left"))
        self.navBar.addAction(back)
        
        forward = QAction("forward", self)
        forward.triggered.connect(self.go_forward)
        forward.setShortcut(QKeySequence("Alt+Right"))
        self.navBar.addAction(forward)
        
        close = QAction("close", self)
        close.triggered.connect(self.close_everything)
        close.setShortcut(QKeySequence("Ctrl+W"))
        self.navBar.addAction(close)
        
        switch = QAction("switch", self)
        switch.triggered.connect(self.switch_windows)
        switch.setShortcut(QKeySequence("Ctrl+D"))
        self.navBar.addAction(switch)
        
        home_btn = QAction("home", self)
        home_btn.triggered.connect(self.go_home)
        home_btn.setShortcut(QKeySequence("Ctrl+E"))
        self.navBar.addAction(home_btn)
        
        switch_btn = QAction("switch", self)
        switch_btn.triggered.connect(self.switch_back)
        switch_btn.setShortcut(QKeySequence("Ctrl+F"))
        self.navBar.addAction(switch_btn)
        
        self.widget = QWidget()
        self.scrollArea = QScrollArea()
        self.readerWidget = QWidget()
        self.popup.setCentralWidget(self.readerWidget)
        self.readerWidget.setLayout(QVBoxLayout())
        self.readerWidget.layout().addWidget(self.navBar)
        self.readerWidget.layout().addWidget(self.stacked)
        self.stacked.addWidget(self.scrollArea)
        self.stacked.addWidget(self.readingList)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())

        self.popup.show()
        self.setVisible(False)
        self.images = []
        forward_url = driver.find_element(By.CLASS_NAME, "nav.next").get_attribute("href")
        print("owoowow", forward_url)
        self.preload_data = []
        self.thread = QThread()
        self.worker = Worker(forward_url, driver)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.fixThread)
        #self.worker.finished.connect(self.worker.deleteLater)
        #self.worker.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_preload)
        
        self.thread.start()
        
        for link in imageLinks:
            image = QImage()
            start_time = time.perf_counter()
            image.loadFromData(requests.get(link).content)
            end_time = time.perf_counter()
            print(f"time taken to loadfromdata = {end_time - start_time}")
            image = image.scaled(int(image.width()*1.15), int(image.height()*1.15))
            img1 = QLabel()
            start_time = time.perf_counter()
            img1.setPixmap(QPixmap(image))
            end_time = time.perf_counter()
            print(f"time taken to setPixmap = {end_time - start_time}")
            self.images.append(img1)
            self.widget.layout().addWidget(img1)
    
    def fixThread(self):
        self.thread.quit()
        self.worker.deleteLater()
        while True:
            if not self.thread.isRunning():
                print("deleting thread")
                self.thread.deleteLater()
                break
    
    def preload(self, forward_url):
        preload_driver = webdriver.Firefox(service=Service(abs_path + "\\temp_images\geckodriver copy.exe"))
        preload_driver.install_addon(r"Python/Comic Reader/adblock.xpi", temporary=True)
        print(forward_url)
        preload_driver.get(forward_url)
        
        images = []
        i = 1
        try:
            while True:
                image = driver.find_element(By.XPATH, f"//*[@id='divImage']/p[{i}]/img").get_attribute("src")
                images.append(image)
                i += 1
        except Exception as e:
            print(e)
            
        preload_driver.quit()
        preload_data = []
        for i, img in enumerate(images):
            response = requests.get(img, stream=True)
            with open(f'img{i}.png', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        
        
    
    def switch_back(self):
        self.popup.close()
        driver.get(driver.current_url.rsplit("/", 2)[0])
        self.setVisible(True)
        
    def bring_up_last(self):
        with open("lasturl.txt", "r") as file:
            link = file.read()
            
        driver.get(link)
    
    def switch_windows(self):
        if self.stacked.currentIndex() == 0:
            self.stacked.setCurrentIndex(1)
        else:
            self.stacked.setCurrentIndex(0)
    
    def go_back(self):
        if self.stacked.currentIndex() == 0:
            back_url = driver.find_element(By.CLASS_NAME, "nav.prev").get_attribute("href")
            driver.get(back_url)
            self.popup.close()
            self.get_images()
        else:
            self.readingList.back()
        
    def drive_forward(self, forward_url):
        driver.get(forward_url)

        
    def go_forward(self):
        if self.stacked.currentIndex() == 0:            
            #print("owo " + forward_url)
            #new_image_data = self.preload_data
            #print("newimg", new_image_data)
            
            #with ProcessPoolExecutor() as executor:
            #    f = executor.submit(self.drive_forward, forward_url)
            
            imgs = []
            forward_url = driver.find_element(By.CLASS_NAME, "nav.next").get_attribute("href")
            print(forward_url)  
            
            for image in self.images:
                image.deleteLater()
                
            self.images = []
            
            for data in self.preload_data:
                img1 = QLabel()
                img1.setPixmap(data)
                self.images.append(img1)
                self.widget.layout().addWidget(img1)
            
            self.scrollArea.verticalScrollBar().setValue(0)

            self.preload_data = []
            self.thread = QThread()
            self.worker = Worker(forward_url, driver)
            self.worker.moveToThread(self.thread)
            
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.fixThread)
            #self.worker.finished.connect(self.worker.deleteLater)
            
            #self.worker.finished.connect(self.thread.deleteLater)
            self.worker.progress.connect(self.update_preload)
            
            self.thread.start()
        else:
            self.readingList.forward()
    
    def update_preload(self, pix):
        print(f"uploaded image #{len(self.preload_data)}")
        self.preload_data.append(pix)
    
    def close_everything(self):
        driver.quit()
        self.popup.close()
        self.close()
        
    def go_home(self):
        if self.stacked.currentIndex() == 0:
            for image in self.images:
                image.deleteLater()
            
            self.images = []
            for data in self.preload_data:
                label = QImage()
                label.loadFromData(data)
                label = label.scaled(int(label.width()*1.15), int(label.height()*1.15))
                img = QLabel()
                img.setPixmap(QPixmap(label))
                self.images.append(img)
                self.widget.layout().addWidget(img)
        else:
            self.readingList.setUrl(QUrl("https://marvelguides.com/comics-introduction"))
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Reader")
    window = MainWindow()
    window.setWindowTitle("Comic Reader")
    sys.exit(app.exec_())
        


