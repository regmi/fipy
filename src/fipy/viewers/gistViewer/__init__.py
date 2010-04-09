__docformat__ = 'restructuredtext'

from gist1DViewer import Gist1DViewer
from gist2DViewer import Gist2DViewer
from gistVectorViewer import GistVectorViewer

__all__ = ["GistViewer", "Gist1DViewer", "Gist2DViewer", "GistVectorViewer"]

def GistViewer(vars, title=None, limits={}, **kwlimits):
    r"""Generic function for creating a `GistViewer`. 
    
    The `GistViewer` factory will search the module tree and return an instance
    of the first `GistViewer` it finds of the correct dimension.
        
    :Parameters:
      vars
        a `CellVariable` or tuple of `CellVariable` objects to plot
      title
        displayed at the top of the `Viewer` window
      limits : dict
        a (deprecated) alternative to limit keyword arguments
      xmin, xmax, ymin, ymax, datamin, datamax
        displayed range of data. A 1D `Viewer` will only use `xmin` and
        `xmax`, a 2D viewer will also use `ymin` and `ymax`. All
        viewers will use `datamin` and `datamax`. Any limit set to a
        (default) value of `None` will autoscale.
    """
    if type(vars) not in [type([]), type(())]:
        vars = [vars]
    
    kwlimits.update(limits)
    
    from fipy.viewers import MeshDimensionError
    
    try:
        return Gist1DViewer(vars=vars, title=title, **kwlimits)
    except MeshDimensionError:
        try:
            return Gist2DViewer(vars=vars, title=title, **kwlimits)
        except MeshDimensionError:
            return GistVectorViewer(vars=vars, title=title, **kwlimits)
            
def make(*args, **kwargs):
    """
    A deprecated synonym for `GistViewer`
    """
    import warnings
    warnings.warn("'GistViewer' should be used instead of 'make'", DeprecationWarning, stacklevel=2)
    return GistViewer(*args, **kwargs)
