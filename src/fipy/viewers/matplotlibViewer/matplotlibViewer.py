#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "matplotlibViewer.py"
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

from fipy.viewers.viewer import _Viewer

class _MatplotlibViewer(_Viewer):
    """
    .. attention:: This class is abstract. Always create one of its subclasses.

    The `_MatplotlibViewer` is the base class for the viewers that use the
    Matplotlib_ python plotting package.

    .. _Matplotlib: http://matplotlib.sourceforge.net/

    """
        
    def __init__(self, vars, title=None, figaspect=1.0, **kwlimits):
        """
        Create a `_MatplotlibViewer`.
        
        :Parameters:
          vars
            a `CellVariable` or tuple of `CellVariable` objects to plot
          title
            displayed at the top of the `Viewer` window
          figaspect
            desired aspect ratio of figure. If arg is a number, use that aspect
            ratio. If arg is an array, figaspect will determine the width and
            height for a figure that would fit array preserving aspect ratio.
          xmin, xmax, ymin, ymax, datamin, datamax
            displayed range of data. A 1D `Viewer` will only use `xmin` and
            `xmax`, a 2D viewer will also use `ymin` and `ymax`. All
            viewers will use `datamin` and `datamax`. Any limit set to a
            (default) value of `None` will autoscale.
        """
        if self.__class__ is _MatplotlibViewer:
            raise NotImplementedError, "can't instantiate abstract base class"
            
        _Viewer.__init__(self, vars=vars, title=title, **kwlimits)

        import pylab

        pylab.ion()

        w, h = pylab.figaspect(figaspect)
        fig = pylab.figure(figsize=(w, h))
        self.id = fig.number
        
        pylab.title(self.title)
        
    def plot(self, filename = None):
        import pylab

        pylab.figure(self.id)

        pylab.ioff()
        
        self._plot()
        pylab.draw()
        
        pylab.ion()

        if filename is not None:
            pylab.savefig(filename)

    def _validFileExtensions(self):
        import pylab
        return ["""
        Matplotlib has no reliable way to determine 
        valid file extensions. Either guess, or see
        <http://matplotlib.sourceforge.net/faq/installing_faq.html#backends> 
        and then guess. Yes, this is lame.
        """]
        
#         filetypes = pylab.figure(self.id).canvas.filetypes
#         return [".%s" % key for key in filetypes.keys()]
        
