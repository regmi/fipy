#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "metalIonDiffusionEquation.py"
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
 # protection and is in the public domain.  PFM is an experimental
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


from fipy.terms.implicitSourceTerm import ImplicitSourceTerm
from fipy.models.levelSet.distanceFunction.levelSetDiffusionEquation import _buildLevelSetDiffusionEquation
from metalIonSourceVariable import _MetalIonSourceVariable

def buildMetalIonDiffusionEquation(ionVar = None,
                                   distanceVar = None,
                                   depositionRate = 1,
                                   transientCoeff = 1,
                                   diffusionCoeff = 1,
                                   metalIonMolarVolume = 1):

    r"""

    The `MetalIonDiffusionEquation` solves the diffusion of the metal
    species with a source term at the electrolyte interface. The governing
    equation is given by,

    .. math::

       \frac{\partial c}{\partial t} = \nabla \cdot D \nabla  c

    where,

    .. math::

       D = \begin{cases}
           D_c & \text{when $\phi > 0$} \\
           0  & \text{when $\phi \le 0$}
       \end{cases}

    The velocity of the interface generally has a linear dependence on ion
    concentration. The following boundary condition applies at the zero
    level set,

    .. math::

       D \hat{n} \cdot \nabla c = \frac{v(c)}{\Omega} \qquad \text{at $phi = 0$}

    where

    .. math::

       v(c) = c V_0

    The test case below is for a 1D steady state problem. The solution is
    given by:

    .. math::

       c(x) = \frac{c^{\infty}}{\Omega D / V_0 + L}\left(x - L\right) + c^{\infty}

    This is the test case,

    >>> from fipy.meshes.grid1D import Grid1D
    >>> nx = 11
    >>> dx = 1.
    >>> from fipy.tools import serial
    >>> mesh = Grid1D(nx = nx, dx = dx, parallelModule=serial)
    >>> x, = mesh.getCellCenters()
    >>> from fipy.variables.cellVariable import CellVariable
    >>> ionVar = CellVariable(mesh = mesh, value = 1.)
    >>> from fipy.models.levelSet.distanceFunction.distanceVariable \
    ...     import DistanceVariable
    >>> disVar = DistanceVariable(mesh = mesh, 
    ...                           value = (x - 0.5) - 0.99,
    ...                           hasOld = 1)

    >>> v = 1.
    >>> diffusion = 1.
    >>> omega = 1.
    >>> cinf = 1.
    >>> from fipy.boundaryConditions.fixedValue import FixedValue
    >>> eqn = buildMetalIonDiffusionEquation(ionVar = ionVar,
    ...                                      distanceVar = disVar,
    ...                                      depositionRate = v * ionVar,
    ...                                      diffusionCoeff = diffusion,
    ...                                      metalIonMolarVolume = omega)
    >>> bc = (FixedValue(mesh.getFacesRight(), cinf),)
    >>> for i in range(10):
    ...     eqn.solve(ionVar, dt = 1000, boundaryConditions = bc)
    >>> L = (nx - 1) * dx - dx / 2
    >>> gradient = cinf / (omega * diffusion / v + L)
    >>> answer = gradient * (x - L - dx * 3 / 2) + cinf
    >>> answer[x < dx] = 1
    >>> print ionVar.allclose(answer)
    1

    :Parameters:
      - `ionVar`: The metal ion concentration variable.
      - `distanceVar`: A `DistanceVariable` object.
      - `depositionRate`: A float or a `CellVariable` representing the interface deposition rate.
      - `transientCoeff`: The transient coefficient.
      - `diffusionCoeff`: The diffusion coefficient
      - `metalIonMolarVolume`: Molar volume of the metal ions.

    """

    eq = _buildLevelSetDiffusionEquation(ionVar = ionVar,
                                         distanceVar = distanceVar,
                                         transientCoeff = transientCoeff,
                                         diffusionCoeff = diffusionCoeff)
    
    coeff = _MetalIonSourceVariable(ionVar = ionVar,
                                    distanceVar = distanceVar,
                                    depositionRate = depositionRate,
                                    metalIonMolarVolume = metalIonMolarVolume)

    return eq + ImplicitSourceTerm(coeff)

def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 
