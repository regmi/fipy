#!/usr/bin/env python

## 
 # -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "convectionCoeff.py"
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
 #  
 # ###################################################################
 ##

__docformat__ = 'restructuredtext'

from fipy.tools.numerix import MA
from fipy.tools import numerix

from fipy.tools import numerix
from fipy.tools import vector

from fipy.variables.faceVariable import FaceVariable

class _ConvectionCoeff(FaceVariable):
    """
    
    Convection coefficient for the `ConservativeSurfactantEquation`.
    The coeff only has a value for a negative `distanceVar`.

    """

    def __init__(self, distanceVar):
        """
        
        Simple one dimensional test:

        
           >>> from fipy.variables.cellVariable import CellVariable
           >>> from fipy.meshes.grid2D import Grid2D
           >>> mesh = Grid2D(nx = 3, ny = 1, dx = 1., dy = 1.)
           >>> from fipy.models.levelSet.distanceFunction.distanceVariable import DistanceVariable
           >>> distanceVar = DistanceVariable(mesh, value = (-.5, .5, 1.5))
           >>> ## answer = numerix.zeros((2, mesh._getNumberOfFaces()),'d')
           >>> answer = FaceVariable(mesh=mesh, rank=1, value=0.).getGlobalValue()
           >>> answer[0,7] = -1
           >>> print numerix.allclose(_ConvectionCoeff(distanceVar).getGlobalValue(), answer)
           True

        Change the dimensions:

           >>> mesh = Grid2D(nx = 3, ny = 1, dx = .5, dy = .25)
           >>> distanceVar = DistanceVariable(mesh, value = (-.25, .25, .75))
           >>> answer[0,7] = -.5
           >>> print numerix.allclose(_ConvectionCoeff(distanceVar).getGlobalValue(), answer)
           True

        Two dimensional example:

           >>> mesh = Grid2D(nx = 2, ny = 2, dx = 1., dy = 1.)
           >>> distanceVar = DistanceVariable(mesh, value = (-1.5, -.5, -.5, .5))
            >>> answer = FaceVariable(mesh=mesh, rank=1, value=0.).getGlobalValue()
           >>> answer[1,2] = -.5
           >>> answer[1,3] = -1
           >>> answer[0,7] = -.5
           >>> answer[0,10] = -1
           >>> print numerix.allclose(_ConvectionCoeff(distanceVar).getGlobalValue(), answer)
           True

        Larger grid:

           >>> mesh = Grid2D(nx = 3, ny = 3, dx = 1., dy = 1.)
           >>> distanceVar = DistanceVariable(mesh, value = (1.5, .5 , 1.5,
           ...                                           .5 , -.5, .5 ,
           ...                                           1.5, .5 , 1.5))
            >>> answer = FaceVariable(mesh=mesh, rank=1, value=0.).getGlobalValue()
           >>> answer[1,4] = .25
           >>> answer[1,7] = -.25
           >>> answer[0,17] = .25
           >>> answer[0,18] = -.25
           >>> print numerix.allclose(_ConvectionCoeff(distanceVar).getGlobalValue(), answer)
           True
           
        """
        
        FaceVariable.__init__(self, mesh=distanceVar.getMesh(), name='surfactant convection', rank=1)
        self.distanceVar = self._requires(distanceVar)

    def _calcValue(self):

        Ncells = self.mesh.getNumberOfCells()
        Nfaces = self.mesh._getNumberOfFaces()
        M = self.mesh._getMaxFacesPerCell()
        dim = self.mesh.getDim()
        cellFaceIDs = self.mesh._getCellFaceIDs()
     
        faceNormalAreas = self.distanceVar._getLevelSetNormals() * self.mesh._getFaceAreas()

        cellFaceNormalAreas = numerix.array(MA.filled(numerix.take(faceNormalAreas, cellFaceIDs, axis=-1), 0))
        norms = numerix.array(MA.filled(MA.array(self.mesh._getCellNormals()), 0))
        
        alpha = numerix.dot(cellFaceNormalAreas, norms)
        alpha = numerix.where(alpha > 0, alpha, 0)

        alphasum = numerix.sum(alpha, axis=0)
        alphasum += (alphasum < 1e-100) * 1.0
        alpha = alpha / alphasum

        phi = numerix.repeat(self.distanceVar[numerix.newaxis, ...], M, axis=0)
        alpha = numerix.where(phi > 0., 0, alpha)
        
        volumes = numerix.array(self.mesh.getCellVolumes())
        alpha = alpha * volumes * norms

        value = numerix.zeros((dim, Nfaces),'d')

        vector._putAddPy(value, cellFaceIDs, alpha, mask=MA.getmask(MA.array(cellFaceIDs)))

##         value = numerix.reshape(value, (dim, Nfaces, dim))

        return -value / self.mesh._getFaceAreas()

def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 
