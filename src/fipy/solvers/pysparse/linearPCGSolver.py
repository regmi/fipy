#!/usr/bin/env python

## 
 # -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "linearPCGSolver.py"
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

import sys

from pysparse import precon
from pysparse import itsolvers

from fipy.solvers.pysparse.pysparseSolver import PysparseSolver

class LinearPCGSolver(PysparseSolver):
    """
    
    The `LinearPCGSolver` solves a linear system of equations using the
    preconditioned conjugate gradient method (PCG) with symmetric successive
    over-relaxation (SSOR) preconditioning.  The PCG method solves systems with
    a symmetric positive definite coefficient matrix.

    The `LinearPCGSolver` is a wrapper class for the the PySparse_
    `itsolvers.pcg()` and `precon.ssor()` methods.

    .. _PySparse: http://pysparse.sourceforge.net
    
    """
     
    def _solve_(self, L, x, b):
##      print 'L:',L
##      print 'x:',x
##      print 'b:',b
##      raw_input('end output')
    
        A = L._getMatrix().to_sss()

        Assor=precon.ssor(A)

        info, iter, relres = itsolvers.pcg(A, b, x, self.tolerance, self.iterations, Assor)
##        print info, iter, relres

        self._raiseWarning(info, iter, relres)
            
    def _canSolveAsymmetric(self):
        return False
                
