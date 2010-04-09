#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "matplotlib1DViewer.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This software was developed at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this software is not subject to copyright
 # protection and is in the public domain.  FiPy is an experimental
 # system.  NIST assumes no responsibility whatsoever for its use by
 # other parties, and makes no guarantees, expressed or implied, about
 # its quality, reliability, or any other characteristic.  We would
 # appreciate acknowledgement if the software is used.
 # 
 # This software can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  See the file "license.terms" for information on usage and  redistribution
 #  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
 #  
 # ###################################################################
 ##
 
__docformat__ = 'restructuredtext'

from matplotlibViewer import _MatplotlibViewer

class Matplotlib1DViewer(_MatplotlibViewer):
    """
    Displays a y vs.  x plot of one or more 1D `CellVariable` objects using
    Matplotlib_.
    
    .. _Matplotlib: http://matplotlib.sourceforge.net/
    """
    
    __doc__ += _MatplotlibViewer._test1D(viewer="Matplotlib1DViewer")
    
    def __init__(self, vars, title=None, xlog=False, ylog=False, limits={}, **kwlimits):
        """
        
        :Parameters:
          vars
            a `CellVariable` or tuple of `CellVariable` objects to plot
          title
            displayed at the top of the `Viewer` window
          xlog
            log scaling of x axis if `True`
          ylog
            log scaling of y axis if `True`
          limits : dict
            a (deprecated) alternative to limit keyword arguments
          xmin, xmax, datamin, datamax
            displayed range of data. Any limit set to 
            a (default) value of `None` will autoscale.
            (*ymin* and *ymax* are synonyms for *datamin* and *datamax*).
        """
        kwlimits.update(limits)
        _MatplotlibViewer.__init__(self, vars=vars, title=title, **kwlimits)
    
        import pylab
        
        if xlog and ylog:
            self.lines = [pylab.loglog(*datum) for datum in self._getData()]
        elif xlog:
            self.lines = [pylab.semilogx(*datum) for datum in self._getData()]
        elif ylog:
            self.lines = [pylab.semilogy(*datum) for datum in self._getData()]
        else:
            self.lines = [pylab.plot(*datum) for datum in self._getData()]

        pylab.legend([var.getName() for var in self.vars])

        pylab.xlim(xmin = self._getLimit('xmin'),
                   xmax = self._getLimit('xmax'))

        ymin = self._getLimit(('datamin', 'ymin'))
        ymax = self._getLimit(('datamax', 'ymax'))
        pylab.ylim(ymin=ymin, ymax=ymax)

        if ymax is None or ymin is None:
            import warnings
            warnings.warn("Matplotlib1DViewer efficiency is improved by setting the 'datamax' and 'datamin' keys", UserWarning, stacklevel=2)

    def _getData(self):
        from fipy.tools.numerix import array
        return [[array(var.getMesh().getCellCenters()[0]), array(var)] for var in self.vars]
            
    def _getSuitableVars(self, vars):
        vars = [var for var in _MatplotlibViewer._getSuitableVars(self, vars) if var.getMesh().getDim() == 1]
        if len(vars) > 1:
            vars = [var for var in vars if var.getMesh() is vars[0].getMesh()]
        if len(vars) == 0:
            from fipy.viewers import MeshDimensionError
            raise MeshDimensionError, "Can only plot 1D data"
        return vars

    def _plot(self):
        ymin, ymax = self._autoscale(vars=self.vars, 
                                     datamin=self._getLimit(('datamin', 'ymin')), 
                                     datamax=self._getLimit(('datamax', 'ymax')))

        import pylab                       
        pylab.ylim(ymin=ymin, ymax=ymax)

        for line, datum in zip(self.lines, self._getData()):
            line[0].set_xdata(datum[0])
            line[0].set_ydata(datum[1])
            
if __name__ == "__main__": 
    import fipy.tests.doctestPlus
    fipy.tests.doctestPlus.execButNoTest()