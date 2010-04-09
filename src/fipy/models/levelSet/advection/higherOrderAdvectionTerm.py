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

from fipy.tools.numerix import MA
from fipy.tools import numerix

from advectionTerm import _AdvectionTerm
from fipy.tools import numerix

class _HigherOrderAdvectionTerm(_AdvectionTerm):
    r"""

    The `_HigherOrderAdvectionTerm` object constructs the `b` vector contribution for
    the advection term given by

    .. math::
    
       u \abs{\nabla \phi}

    from the advection equation given by:

    .. math::

       \frac{\partial \phi}{\partial t} + u \abs{\nabla \phi} = 0

    The construction of the gradient magnitude term requires upwinding as in the standard
    `_AdvectionTerm`. The higher order terms are incorperated as follows.
    The formula used here is given by:

    .. math::

       u_P \abs{\nabla \phi}_P = \max \left( u_P , 0 \right) \left[  \sum_A \min \left( D_{AP}, 0 \right)^2 \right]^{1/2} +  \min \left( u_P , 0 \right) \left[  \sum_A \max \left( D_{AP}, 0 \right)^2 \right]^{1/2}

    where,

    .. math::

       D_{AP} = \frac{ \phi_A - \phi_P } { d_{AP}} - \frac{ d_{AP} } {2} m \left(L_A, L_P \right)

    and

    .. math::

       m\left(x, y\right) &= x \qquad \text{if $\abs{x} \le \abs{y} \forall xy \ge 0$} \\
       m\left(x, y\right) &= y \qquad \text{if $\abs{x} > \abs{y} \forall xy \ge 0$} \\
       m\left(x, y\right) &= 0 \qquad \text{if $xy < 0$}
    
    also,

    .. math::

       L_A &= \frac{\phi_{AA} + \phi_P - 2 \phi_A}{d_{AP}^2} \\
       L_P &= \frac{\phi_{A} + \phi_{PP} - 2 \phi_P}{d_{AP}^2}

    Here are some simple test cases for this problem:

    >>> from fipy.meshes.grid1D import Grid1D
    >>> from fipy.solvers import *
    >>> from fipy.tools import parallel
    >>> SparseMatrix = LinearPCGSolver()._getMatrixClass()
    >>> mesh = Grid1D(dx = 1., nx = 3) 
   
    Trivial test:

    >>> from fipy.variables.cellVariable import CellVariable
    >>> coeff = CellVariable(mesh = mesh, value = numerix.zeros(3, 'd'))
    >>> L, b = _HigherOrderAdvectionTerm(0.)._buildMatrix(coeff, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.zeros(3, 'd'), atol = 1e-10)
    True
   
    Less trivial test:

    >>> coeff = CellVariable(mesh = mesh, value = numerix.arange(3))
    >>> L, b = _HigherOrderAdvectionTerm(1.)._buildMatrix(coeff, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.array((0., -1., -1.)), atol = 1e-10)
    True

    Even less trivial

    >>> coeff = CellVariable(mesh = mesh, value = numerix.arange(3)) 
    >>> L, b = _HigherOrderAdvectionTerm(-1.)._buildMatrix(coeff, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, numerix.array((1., 1., 0.)), atol = 1e-10)
    True

    Another trivial test case (more trivial than a trivial test case
    standing on a harpsichord singing 'trivial test cases are here again')

    >>> vel = numerix.array((-1, 2, -3))
    >>> coeff = CellVariable(mesh = mesh, value = numerix.array((4,6,1))) 
    >>> L, b = _HigherOrderAdvectionTerm(vel)._buildMatrix(coeff, SparseMatrix)
    >>> print parallel.procID > 0 or numerix.allclose(b, -vel * numerix.array((2, numerix.sqrt(5**2 + 2**2), 5)), atol = 1e-10)
    True

    Somewhat less trivial test case:

    >>> from fipy.meshes.grid2D import Grid2D
    >>> mesh = Grid2D(dx = 1., dy = 1., nx = 2, ny = 2)
    >>> vel = numerix.array((3, -5, -6, -3))
    >>> coeff = CellVariable(mesh = mesh, value = numerix.array((3 , 1, 6, 7)))
    >>> L, b = _HigherOrderAdvectionTerm(vel)._buildMatrix(coeff, SparseMatrix)
    >>> answer = -vel * numerix.array((2, numerix.sqrt(2**2 + 6**2), 1, 0))
    >>> print parallel.procID > 0 or numerix.allclose(b, answer, atol = 1e-10)
    True

    For the above test cases the `_HigherOrderAdvectionTerm` gives the
    same result as the `_AdvectionTerm`. The following test imposes a quadratic
    field. The higher order term can resolve this field correctly.

    .. math::

       \phi = x^2

    The returned vector ``b`` should have the value:

    .. math::

       -\abs{\nabla \phi} = -\left|\frac{\partial \phi}{\partial x}\right| = - 2 \abs{x}

    Build the test case in the following way,

    >>> mesh = Grid1D(dx = 1., nx = 5)
    >>> vel = 1.
    >>> coeff = CellVariable(mesh = mesh, value = mesh.getCellCenters()[0]**2)
    >>> L, b = _AdvectionTerm(vel)._buildMatrix(coeff, SparseMatrix)
        
    The first order term is not accurate. The first and last element are ignored because they
    don't have any neighbors for higher order evaluation

    >>> print numerix.allclose(CellVariable(mesh=mesh, value=b).getGlobalValue()[1:-1], -2 * mesh.getCellCenters().getGlobalValue()[0][1:-1])
    False

    The higher order term is spot on.

    >>> L, b = _HigherOrderAdvectionTerm(vel)._buildMatrix(coeff, SparseMatrix)
    >>> print numerix.allclose(b[1:-1], -2 * mesh.getCellCenters()[0][1:-1])
    True

    The `_HigherOrderAdvectionTerm` will also resolve a circular field with
    more accuracy,

    .. math::

       \phi = \left( x^2 + y^2 \right)^{1/2}

    Build the test case in the following way,

    >>> mesh = Grid2D(dx = 1., dy = 1., nx = 10, ny = 10)
    >>> vel = 1.
    >>> x, y = mesh.getCellCenters()
    >>> r = numerix.sqrt(x**2 + y**2)
    >>> coeff = CellVariable(mesh = mesh, value = r)
    >>> L, b = _AdvectionTerm(1.)._buildMatrix(coeff, SparseMatrix)
    >>> error = CellVariable(mesh=mesh, value=b + 1)
    >>> ans = CellVariable(mesh=mesh, value=b + 1)
    >>> ans[(x > 2) & (x < 8) & (y > 2) & (y < 8)] = 0.123105625618
    >>> print (error <= ans).all()
    True

    The maximum error is large (about 12 %) for the first order advection.

    >>> L, b = _HigherOrderAdvectionTerm(1.)._buildMatrix(coeff, SparseMatrix)
    >>> error = CellVariable(mesh=mesh, value=b + 1)
    >>> ans = CellVariable(mesh=mesh, value=b + 1)
    >>> ans[(x > 2) & (x < 8) & (y > 2) & (y < 8)] = 0.0201715476598
    >>> print (error <= ans).all()
    True

    The maximum error is 2 % when using a higher order contribution.

    """
    def _getDifferences(self, adjacentValues, cellValues, oldArray, cellToCellIDs, mesh):
        
        dAP = mesh._getCellToCellDistances()
        
##        adjacentGradient = numerix.take(oldArray.getGrad(), cellToCellIDs)
        adjacentGradient = numerix.take(oldArray.getGrad(), mesh._getCellToCellIDs(), axis=-1)
        adjacentNormalGradient = numerix.dot(adjacentGradient, mesh._getCellNormals())
        adjacentUpValues = cellValues + 2 * dAP * adjacentNormalGradient

        cellIDs = numerix.repeat(numerix.arange(mesh.getNumberOfCells())[numerix.newaxis, ...], mesh._getMaxFacesPerCell(), axis=0)
        cellIDs = MA.masked_array(cellIDs, mask = MA.getmask(mesh._getCellToCellIDs()))
        cellGradient = numerix.take(oldArray.getGrad(), cellIDs, axis=-1)
        cellNormalGradient = numerix.dot(cellGradient, mesh._getCellNormals())
        cellUpValues = adjacentValues - 2 * dAP * cellNormalGradient
        
        cellLaplacian = (cellUpValues + adjacentValues - 2 * cellValues) / dAP**2

        adjacentLaplacian = (adjacentUpValues + cellValues - 2 * adjacentValues) / dAP**2
        adjacentLaplacian = adjacentLaplacian.filled(0)
        cellLaplacian = cellLaplacian.filled(0)

        mm = numerix.where(cellLaplacian * adjacentLaplacian < 0.,
                           0.,
                           numerix.where(abs(cellLaplacian) > abs(adjacentLaplacian),
                                         adjacentLaplacian,
                                         cellLaplacian))
        
        return _AdvectionTerm._getDifferences(self, adjacentValues, cellValues, oldArray, cellToCellIDs, mesh) -  mm * dAP / 2.

def _test(): 
    import doctest
    return doctest.testmod()

if __name__ == "__main__":
    _test()
        
        

    


        

    

    
      

        
        
        
        
