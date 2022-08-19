# Hidden Browser with selenium to nav webpage with the custom gui
from re import S
from tokenize import group
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import os
import sys
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtWidgets import QStackedWidget, QMainWindow, QApplication, QLabel, QPushButton, QGridLayout, QVBoxLayout, QWidget, QLineEdit, QListWidget, QHBoxLayout, QScrollArea, QToolBar, QAction
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QKeySequence, QFont, QImage, QPixmap
from adblockparser import AdblockRules
from PyQt5.QtWebEngineCore import *
from PyQt5.uic import loadUi
import requests

abs_path = os.path.dirname(__file__)

driver = webdriver.Firefox(service=Service(abs_path + "\geckodriver.exe"))
driver.get("https://readcomiconline.li")

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

        # Main Window
        self.setMinimumSize(800, 500)
        self.show()
        
    def search_comic(self):
        searchBar = driver.find_element(By.ID, "keyword")
        searchBar.send_keys(self.search.text())
        searchButton = driver.find_element(By.ID, "imgSearch")
        searchButton.click()
        self.get_comics()
        
    def get_comics(self):
        i = 1
        try:
            while True:
                title = driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div[1]/div/div[2]/div/div[5]/div[{i}]").get_attribute("title").split(">", 1)[1].split("<", 1)[0]
                self.comicList.addItem(title)
                i += 1
        except:
            pass
    
    def go_to_comic(self):
        chosen = self.comicList.currentItem().text()
        i = 1
        try:
            while True:
                title = driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div[1]/div/div[2]/div/div[5]/div[{i}]").get_attribute("title").split(">", 1)[1].split("<", 1)[0]
                if title == chosen:
                    break
                i += 1
        except:
            pass
        
        url = driver.find_element(By.XPATH, f"/html/body/div[1]/div[4]/div[1]/div/div[2]/div/div[5]/div[{i}]/a").get_attribute("href")
        driver.get(url)
        
        self.get_issues()
        
    def get_issues(self):
        i = 3
        try:
            while True:
                title = driver.find_element(By.XPATH, f"//*[@id='leftside']/div[3]/div[2]/div/table/tbody/tr[{i}]/td[1]/a").get_attribute("title").replace(" comic online in high quality", "")
                self.issueList.addItem(title)
                i += 1
        except:
            pass
        
    def go_to_issue(self):
        i = 3
        chosen = self.issueList.currentItem().text()
        try:
            while True:
                title = driver.find_element(By.XPATH, f"//*[@id='leftside']/div[3]/div[2]/div/table/tbody/tr[{i}]/td[1]/a").get_attribute("title").replace(" comic online in high quality", "")
                if chosen == title:
                    break
                i += 1
        except:
            pass
    
        url = driver.find_element(By.XPATH, f"//*[@id='leftside']/div[3]/div[2]/div/table/tbody/tr[{i}]/td[1]/a").get_attribute("href")
        driver.get(url + "&readType=1")
        
        self.get_images()
        
    def get_images(self):
        images = []
        i = 1
        try:
            while True:
                image = driver.find_element(By.XPATH, f"//*[@id='divImage']/p[{i}]/img").get_attribute("src")
                images.append(image)
                i += 1
        except:
            pass
        
        self.display_comic(images)
        
    def display_comic(self, imageLinks):
        print("hewo")
        self.window = QMainWindow()
        self.window.setBaseSize(800, 1800)
        self.navBar = QToolBar("Nav")
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
        
        
        self.widget = QWidget()
        self.scrollArea = QScrollArea()
        self.readerWidget = QWidget()
        self.window.setCentralWidget(self.readerWidget)
        self.readerWidget.setLayout(QVBoxLayout())
        self.readerWidget.layout().addWidget(self.navBar)
        self.readerWidget.layout().addWidget(self.scrollArea)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.widget)
        self.widget.setLayout(QVBoxLayout())
        self.window.setWindowFlag(Qt.FramelessWindowHint)
        self.window.setMinimumSize(1200, 1800)

        self.window.show()
        self.setVisible(False)
        images = []
        for link in imageLinks:
            image = QImage()
            image.loadFromData(requests.get(link).content)
            image = image.scaled(int(image.width()*1.15), int(image.height()*1.15))
            img1 = QLabel()
            img1.setPixmap(QPixmap(image))
            self.widget.layout().addWidget(img1)
            
    def go_back(self):
        back_url = driver.find_element(By.XPATH, "//*[@id='containerRoot']/div[4]/div[1]/div/a[1]").get_attribute("href")
        driver.get(back_url + "&readType=1")
        self.window.close()
        self.get_images()
        
    def go_forward(self):
        forward_url = driver.find_element(By.XPATH, "//*[@id='containerRoot']/div[4]/div[1]/div/a[2]").get_attribute("href")
        driver.get(forward_url + "&readType=1")
        self.window.close()
        self.get_images()
        
    def close_everything(self):
        driver.quit()
        self.window.close()
        self.close()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Reader")
    window = MainWindow()
    window.setWindowTitle("Comic Reader")
    sys.exit(app.exec_())
        


