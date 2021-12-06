'''
Utility functions.
'''

import matplotlib.pyplot as plt

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
