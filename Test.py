from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
import time
import urllib.request
import os
import selenium
from time import sleep

browser = webdriver.Chrome("D:\chromedriver.exe")
browser.get("https://b-care-56aec.web.app/home")

sleep(5)
login = browser.find_element_by_xpath("//*[@id='navbarSupportedContent']/ul/li[1]/a/button")
login.click()
sleep(5)
username = browser.find_element_by_xpath("//*[@id='email']")
username.send_keys("vijayjeyakumar@gmail.com")
sleep(1)
password = browser.find_element_by_xpath("//*[@id='password']")
password.send_keys("vijay123")

browser.find_element_by_xpath("//*[@id='mat-tab-content-0-0']/div/div/div/div/div[2]/form/div[4]/input").click()
sleep(5)



#To test Register

browser.find_element_by_xpath("//*[@id='mat-tab-label-0-1']/div").click()
sleep(5)
browser.find_element_by_xpath("//*[@id='userName']").send_keys("Velu Srinath")
browser.find_element_by_xpath("//*[@id='emailId']").send_keys("velu@gmail.com")
browser.find_element_by_xpath("//*[@id='password']").send_keys("velu123")
browser.find_element_by_xpath("//*[@id='cpassword']").send_keys("velu123")
browser.find_element_by_xpath("//*[@id='mat-tab-content-0-1']/div/div/div/div/div[2]/form/div[5]/input").click()


browser.close()



