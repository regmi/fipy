#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "trilinosSolver.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #  Author: Maxsim Gibiansky <maxsim.gibiansky@nist.gov>
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

from fipy.solvers.solver import Solver
from fipy.tools.trilinosMatrix import _TrilinosMatrix
from fipy.tools.pysparseMatrix import _PysparseMatrix
from fipy.tools.trilinosMatrix import _numpyToTrilinosVector
from fipy.tools.trilinosMatrix import _trilinosToNumpyVector

from PyTrilinos import Epetra
from PyTrilinos import EpetraExt

from fipy.tools import numerix

class TrilinosSolver(Solver):

    """
    .. attention:: This class is abstract. Always create one of its subclasses.

    """
    def __init__(self, *args, **kwargs):
        if self.__class__ is TrilinosSolver:
            raise NotImplementedError, "can't instantiate abstract base class"
        else:
            Solver.__init__(self, *args, **kwargs)
            
    def _storeMatrix(self, var, matrix, RHSvector):
        self.var = var
        self.matrix = matrix
        self.RHSvector = RHSvector
        
    def _buildGlobalMatrix(self):
        
        matrix = self.matrix
        RHSvector = self.RHSvector
    
        mesh = self.var.getMesh()
        comm = Epetra.PyComm()
        
        globalNonOverlappingCellIDs = mesh._getGlobalNonOverlappingCellIDs()
        globalOverlappingCellIDs = mesh._getGlobalOverlappingCellIDs()
        localNonOverlappingCellIDs = mesh._getLocalNonOverlappingCellIDs()
        localOverlappingCellIDs = mesh._getLocalOverlappingCellIDs()
        
        self.nonOverlappingMap = Epetra.Map(-1, list(globalNonOverlappingCellIDs), 0, comm)
        self.nonOverlappingVector = Epetra.Vector(self.nonOverlappingMap, 
                                                  self.var[localNonOverlappingCellIDs])
        
        self.nonOverlappingRHSvector = Epetra.Vector(self.nonOverlappingMap, 
                                                     RHSvector[localNonOverlappingCellIDs])

        self.globalMatrix = Epetra.CrsMatrix(Epetra.Copy, self.nonOverlappingMap, -1)

        localNonOverlappingCellIDsMask = numerix.zeros(len(localOverlappingCellIDs), 'int')
        localNonOverlappingCellIDsMask[localNonOverlappingCellIDs] = 1
        A = matrix.matrix.copy()
        A.delete_rows(localNonOverlappingCellIDsMask)

        values, irow, jcol = A.find()
        
        globalNonOverlappingCellIDsIrow = globalNonOverlappingCellIDs[irow]
        if hasattr(globalNonOverlappingCellIDsIrow, 'astype') and \
               globalNonOverlappingCellIDsIrow.dtype.name == 'int64':
            globalNonOverlappingCellIDsIrow = globalNonOverlappingCellIDsIrow.astype('int32')

        globalOverlappingCellIDsJcol = globalOverlappingCellIDs[jcol]
        if hasattr(globalOverlappingCellIDsJcol, 'astype') and \
               globalOverlappingCellIDsJcol.dtype.name == 'int64':
            globalOverlappingCellIDsJcol = globalOverlappingCellIDsJcol.astype('int32')
        
        
        self.globalMatrix.InsertGlobalValues(globalNonOverlappingCellIDsIrow, 
                                             globalOverlappingCellIDsJcol, 
                                             values)
        
        self.globalMatrix.FillComplete()
        self.globalMatrix.OptimizeStorage()
        
        self.overlappingMap =  Epetra.Map(-1, list(globalOverlappingCellIDs), 0, comm)
        self.overlappingVector = Epetra.Vector(self.overlappingMap, self.var)


    def _solve(self):

        if not hasattr(self, 'globalMatrix'):
            self._buildGlobalMatrix()
        
        self._solve_(self.globalMatrix, 
                     self.nonOverlappingVector, 
                     self.nonOverlappingRHSvector)

        self.overlappingVector.Import(self.nonOverlappingVector, 
                                      Epetra.Import(self.overlappingMap, 
                                                    self.nonOverlappingMap), 
                                      Epetra.Insert)
        
        self.var.setValue(self.overlappingVector)

        del self.globalMatrix
        del self.matrix
        del self.RHSvector
        del self.var
            
    def _getMatrixClass(self):
        # an ugly expediency (I blame Wheeler)
        return _PysparseMatrix

    def _calcResidualVector(self, residualFn=None):
        if residualFn is not None:
            return residualFn(self.var, self.matrix, self.RHSvector)
        else:
            if not hasattr(self, 'globalMatrix'):
                self._buildGlobalMatrix()
            residual = Epetra.Vector(self.nonOverlappingMap)                
            self.globalMatrix.Multiply(False, self.nonOverlappingVector, residual)
            residual -= self.nonOverlappingRHSvector
          
            return residual

    def _calcResidual(self, residualFn=None):
        if residualFn is not None:
            return residualFn(self.var, self.matrix, self.RHSvector)
        else:
            return self._calcResidualVector().Norm2()
        
    def _calcRHSNorm(self):
        return self.nonOverlappingRHSvector.Norm2()
