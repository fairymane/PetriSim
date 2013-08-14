#import wx
import petrinet # just to get version number and correct version of wx 

from setuptools import setup 

Plist={} 

APP = ['petrinet.py'] 
DATA_FILES = [] 
OPTIONS = {'argv_emulation': True, # this puts the names of dropped files into sys.argv when starting the app. 
            #'iconfile': 'Icons/ConverterIcon.icns', 
	    'includes' :['wx'],
	    #'modules' :['wx'],	
            'plist': Plist, 
            } 


setup( 
     app=APP, 
     data_files=DATA_FILES, 
     #version=petrinet.__version__, 
     description="Petrinet GUI utility", 
     author="Tao Feng", 
     #author_email="[hidden email]", 
     options={'py2app': OPTIONS}, 
     setup_requires=['py2app'], 
) 
