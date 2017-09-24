import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

class PlotClass():
    """
    Adapted from the span_selector.py example code
    (see https://matplotlib.org/examples/widgets/span_selector.html).
    Plots multiple datasets and allows user to zoom in on
    a region which is then displayed below the main data.
    """
    def __init__(self, data_list, title="Provide Title"):
        """
        Parameters
        ----------
        data_list: list
            List of 2-tuples of the form (xdata, ydata) where
            xdata and ydata are lists corresponding to
            x and y values to be plotted. xdata and ydata have
            the same length.
            
        title: string
            Title of plot
        """
        self.data_list = data_list
        self.fig = plt.figure(figsize=(8, 6))
        self.axes = self.fig.add_subplot(211)

        for data in self.data_list:
            self.axes.plot(data[0], data[1], '-o')

        self.axes.set_title(title)

        self.axes2 = self.fig.add_subplot(212)
        for data in self.data_list:
            line, = self.axes2.plot(data[0], data[1], '-o')

        self.span = SpanSelector(self.axes, self.onselect, 'horizontal', useblit=True,
                        rectprops=dict(alpha=0.5, facecolor='red'))

    def onselect(self, xmin, xmax):
        tmp_data_list = []
        ymin = 10000000
        ymax = -10000000
        for data in self.data_list:
            if min(data[0]) >= xmin and min(data[0]) <= xmax:
                tmp_data_list.append(data[0])
            elif max(data[0]) >= xmin and max(data[0]) <= xmax:
                tmp_data_list.append(data[0])

        for data in self.data_list:
            indmin, indmax = np.searchsorted(data[0], (xmin, xmax))
            #indmax = min(len(data[0])-1, indmax)
            #if indmin == len(data[0]):
            #    indmin = indmin - 1
                #or indmax == 0:
                #continue
            #else:
            for val in range(indmin, indmax):
                if data[1][val] <= ymin:
                    ymin = data[1][val]
                if data[1][val] >= ymax:
                    ymax = data[1][val]
                    
        self.axes2.set_xlim(xmin, xmax)
        self.axes2.set_ylim(ymin, ymax)
        self.axes.figure.canvas.draw()
        
    def add_data(self, xdata, ydata):
        self.data_list.append((xdata, ydata))
        self.axes.plot(xdata, ydata, '-o')
        self.axes2.plot(xdata, ydata, '-o')
        self.axes.figure.canvas.draw()
        
    def legend(self, legend_list):
        self.axes.legend(legend_list)
        
    def show(self):
        plt.show()