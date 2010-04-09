#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "advectionEquation.py"
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

from fipy.tools import numerix
from fipy.tools.numerix import MA

from fipy.terms.term import Term

class _AdvectionTerm(Term):
    r"""

    The `_AdvectionTerm` object constructs the b vector contribution
    for the advection term given by

    .. math::

       u \abs{\nabla \phi}

    from the advection equation given by:

    .. math::

       \frac{\partial \phi}{\partial t} + u \abs{\nabla \phi} = 0

    The construction of the gradient magnitude term requires upwinding.
    The formula used here is given by:

    .. math::

       u_P \abs{\nabla \phi}_P = \max \left( u_P , 0 \right) \left[  \sum_A \min \left( \frac{ \phi_A - \phi_P } { d_{AP}}, 0 \right)^2 \right]^{1/2} +  \min \left( u_P , 0 \right) \left[  \sum_A \max \left( \frac{ \phi_A - \phi_P } { d_{AP}}, 0 \right)^2 \right]^{1/2}

    Here are some simple test cases for this problem:

    >>> from fipy.meshes.grid1D import Grid1D
    >>> from fipy.solvers import *
    >>> from fipy.tools import parallel
    >>> SparseMatrix = LinearLUSolver()._getMatrixClass()
    >>> mesh = Grid1D(dx = 1., nx = 3) 
    >>> from fipy.variables.cellVariable import CellVariable
   
    Trivial test:

    >>> var = CellVariable(value = numerix.zeros(3, 'd'), mesh = mesh)
    >>> L, b = _AdvectionTerm(0.)._buildMatrix(var, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.zeros(3, 'd'), atol = 1e-10)
    True
   
    Less trivial test:

    >>> var = CellVariable(value = numerix.arange(3), mesh = mesh)
    >>> L, b = _AdvectionTerm(1.)._buildMatrix(var, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.array((0., -1., -1.)), atol = 1e-10)
    True

    Even less trivial

    >>> var = CellVariable(value = numerix.arange(3), mesh = mesh)
    >>> L, b = _AdvectionTerm(-1.)._buildMatrix(var, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.array((1., 1., 0.)), atol = 1e-10)
    True

    Another trivial test case (more trivial than a trivial test case
    standing on a harpsichord singing 'trivial test cases are here again')

    >>> vel = numerix.array((-1, 2, -3))
    >>> var = CellVariable(value = numerix.array((4,6,1)), mesh = mesh)
    >>> L, b = _AdvectionTerm(vel)._buildMatrix(var, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, -vel * numerix.array((2, numerix.sqrt(5**2 + 2**2), 5)), atol = 1e-10)
    True

    Somewhat less trivial test case:

    >>> from fipy.meshes.grid2D import Grid2D
    >>> mesh = Grid2D(dx = 1., dy = 1., nx = 2, ny = 2)
    >>> vel = numerix.array((3, -5, -6, -3))
    >>> var = CellVariable(value = numerix.array((3 , 1, 6, 7)), mesh = mesh)
    >>> L, b = _AdvectionTerm(vel)._buildMatrix(var, SparseMatrix)
    >>> answer = -vel * numerix.array((2, numerix.sqrt(2**2 + 6**2), 1, 0))
    >>> print parallel.procID > 0 or numerix.allclose(b, answer, atol = 1e-10)
    True
    """
    def __init__(self, coeff = None):
        Term.__init__(self)
        self.geomCoeff = coeff
        
    def _buildMatrix(self, var, SparseMatrix, boundaryCondtions=(), dt=None, equation=None):

        oldArray = var.getOld()

        mesh = var.getMesh()
        NCells = mesh.getNumberOfCells()
        NCellFaces = mesh._getMaxFacesPerCell()

        cellValues = numerix.repeat(oldArray[numerix.newaxis, ...], NCellFaces, axis = 0)
        
        cellIDs = numerix.repeat(numerix.arange(NCells)[numerix.newaxis, ...], NCellFaces, axis = 0)
        cellToCellIDs = mesh._getCellToCellIDs()

        if NCells > 0:
            cellToCellIDs = MA.where(MA.getmask(cellToCellIDs), cellIDs, cellToCellIDs) 

            adjacentValues = numerix.take(oldArray, cellToCellIDs)

            differences = self._getDifferences(adjacentValues, cellValues, oldArray, cellToCellIDs, mesh)
            differences = MA.filled(differences, 0)
            
            minsq = numerix.sqrt(numerix.sum(numerix.minimum(differences, numerix.zeros((NCellFaces, NCells)))**2, axis=0))
            maxsq = numerix.sqrt(numerix.sum(numerix.maximum(differences, numerix.zeros((NCellFaces, NCells)))**2, axis=0))

            coeff = numerix.array(self._getGeomCoeff(mesh))

            coeffXdiffereneces = coeff * ((coeff > 0.) * minsq + (coeff < 0.) * maxsq)
        else:
            coeffXdiffereneces = 0.

        return (SparseMatrix(size = NCells), -coeffXdiffereneces * mesh.getCellVolumes())
        
    def _getDifferences(self, adjacentValues, cellValues, oldArray, cellToCellIDs, mesh):
        return (adjacentValues - cellValues) / mesh._getCellToCellDistances()

    def _getDefaultSolver(self, solver, *args, **kwargs):
        if solver and not solver._canSolveAsymmetric():
            import warnings
            warnings.warn("%s cannot solve assymetric matrices" % solver)

        import fipy.solvers.solver
        if fipy.solvers.solver == 'trilinos':
            from fipy.solvers.trilinos.preconditioners.jacobiPreconditioner import JacobiPreconditioner
            from fipy.solvers.trilinos.linearGMRESSolver import LinearGMRESSolver
            return solver or LinearGMRESSolver(precon=JacobiPreconditioner(), *args, **kwargs)
        else:
            from fipy.solvers import DefaultAsymmetricSolver
            return solver or DefaultAsymmetricSolver(*args, **kwargs)



def _test(): 
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()
        
        

    


        

    

    
      

        
        
        
        
