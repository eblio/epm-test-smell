'''
Utility functions.
'''

import glob
import matplotlib.pyplot as plt
from datetime import datetime

SMELL_PATH = '../../data/rq1/android_test_smells/'
NAME_FORMAT = '*_{}_*.csv'

def set_plot_size(w, h, ax=None):
    '''
    Sets the size of the plot.
    https://stackoverflow.com/questions/44970010/axes-class-set-explicitly-size-width-height-of-axes-in-given-units
    '''
    if not ax:
        ax = plt.gca()
        
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom

    figw = float(w)/(r-l)
    figh = float(h)/(t-b)

    ax.figure.set_size_inches(figw, figh)
    

def string_to_date(date_string):
    '''
    Transforms a string to a datetime object.
    '''
    return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')


def name_to_filename(name):
    '''
    Transforms a repository name into a filename.
    '''
    return name.replace('/', '_') + '.json'


def filename_to_name(filename):
    '''
    Transforms a filename to a repository name.
    '''
    return filename.replace('_', '/')[:-5]  # Remove the .json extension


def name_to_project_name(name):
    '''
    Gets the project name based on the repository name (user/project).
    '''
    return name.split("/", 1)[1].replace('/', '_')


def project_name_to_file_name(name):
    '''
    Gets the file corresponding to a certain project name.
    '''
    return glob.glob(SMELL_PATH + NAME_FORMAT.format(name))[0]
