#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "trilinosMatrix.py"
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

from PyTrilinos import Epetra
from PyTrilinos import EpetraExt

from fipy.tools.sparseMatrix import _SparseMatrix
from fipy.tools import numerix

# Current inadequacies of the matrix class:

# 1) Adding matrices - the matrix with fewer nonzeros gets added into the one
# that has more; this works as long as it's nonzero entries are a subset of the
# larger one's nonzero entries. Is true for all cases in fipy, but is not true
# in the general case - this isn't a general matrix class like the pysparse
# matrix class is.
#
# 2) addAt currently not guaranteed to work for fill-completed matrices, if
# elements are being added in new spots.
#
# 3) put currently not guaranteed to work for non-empty matrices that do not
# have all the target spots occupied. 
#
# None of these situations currently come up in FiPy; tests do not reveal any of 
# the warnings that guard for those, and all tests pass. Because of the way
# FiPy constructs its matrices, I do not anticipate any of these occurring. 
#
# 4) Parallelization - currently matrix builds everything on processor 0, to be
# redistributed later. As of now, cannot be done better without putting in
# extremely inefficient filters to filter out unnecessary elements on each
# processor.

class _TrilinosMatrix(_SparseMatrix):
    
    """
    _TrilinosMatrix class wrapper for a PyTrilinos Epetra.CrsMatrix.
    _TrilinosMatrix is always NxN.
    Allows basic python operations __add__, __sub__ etc.
    Facilitate matrix populating in an easy way.
    """

    def __init__(self, size = None, bandwidth = 0, matrix = None, sizeHint = None):
        """
        Creates a `_TrilinosMatrix`.

        :Parameters:
          - `size`: The size N for an N by N matrix.
          - `bandwidth`: The proposed band width of the matrix.
          - `matrix`: The starting `Epetra.CrsMatrix` if there is one.

        """

        if matrix != None:
            self.matrix = matrix
            self.map = matrix.RowMap()
            self.comm = matrix.Comm()
            self.bandwidth = (matrix.NumGlobalNonzeros() + matrix.NumGlobalRows()-1)/matrix.NumGlobalRows()
        else:
            self.comm = Epetra.PyComm()
            if sizeHint is not None and bandwidth == 0:
                self.bandwidth = (sizeHint + size - 1)/size 
            else:
                self.bandwidth = bandwidth
                
            # Matrix building gets done on one processor - it gets the map for
            # all the rows
            if self.comm.MyPID()==0:
                self.map = Epetra.Map(size, range(0, size), 0, self.comm)
            else: 
                self.map = Epetra.Map(size, [], 0, self.comm)

            self.matrix = Epetra.CrsMatrix(Epetra.Copy, self.map, self.bandwidth*3/2)

            # Leave extra bandwidth, to handle multiple insertions into the
            # same spot. It's memory-inefficient, but it'll get cleaned up when
            # FillComplete is called, and according to the Trilinos devs the
            # performance boost will be worth it.

    def _getMatrix(self):
        return self.matrix
    
    # All operations that require getting data out of the matrix may need to
    # call FillComplete to make sure they work.  There will be no warnings when
    # FillComplete is implicitly called; there will only be warnings when
    # insertions fail.
    def copy(self):
        if not self._getMatrix().Filled():
            self._getMatrix().FillComplete()

        return _TrilinosMatrix(matrix = Epetra.CrsMatrix(self.matrix))
            
        
    def __getitem__(self, index):
        if not self.matrix.Filled():
            self._getMatrix().FillComplete()

        return self.matrix[index]
        
    def __str__(self):
        if not self.matrix.Filled():
            self.matrix.FillComplete()
        return _SparseMatrix.__str__(self)

    def __setitem__(self, index, value):
        self.matrix[index] = value
        

    # Addition is tricky. 
    # Trilinos interface is as such: A can be added into B, but A has to be
    # Filled() beforehand. If B is filled beforehand, this may or may not
    # crash, depending on whether things are being added into spots in B that
    # were not there before.  Have put in some order-of-operands twiddling to
    # make it look like two things can be added in any order.

    # Though not guaranteed to work for arbitrary matrices, it should work for
    # all those generated by FiPy and will give warnings if it encounters
    # trouble (unless Trilinos runs into an error and aborts instead of
    # returning an error code)

    def __iadd__(self, other):
        if other != 0:
            if not other._getMatrix().Filled():
                other._getMatrix().FillComplete()
            
            # Depending on which one is more filled, pick the order of operations 
            if self._getMatrix().Filled() and other._getMatrix().NumGlobalNonzeros() \
                                            > self._getMatrix().NumGlobalNonzeros():
                tempBandwidth = other._getMatrix().NumGlobalNonzeros() \
                                 /self._getMatrix().NumGlobalRows()+1

                tempMatrix = Epetra.CrsMatrix(Epetra.Copy, self.map, tempBandwidth)
                
                if EpetraExt.Add(other._getMatrix(), False, 1, tempMatrix, 1) != 0:
                    import warnings
                    warnings.warn("EpetraExt.Add returned error code in __iadd__, 1",
                                   UserWarning, stacklevel=2)

                if EpetraExt.Add(self._getMatrix(), False, 1, tempMatrix, 1) != 0:
                    import warnings
                    warnings.warn("EpetraExt.Add returned error code in __iadd__, 2",
                                   UserWarning, stacklevel=2)

                self.matrix = tempMatrix
                
            else:
                if EpetraExt.Add(other._getMatrix(), False,1,self._getMatrix(),1) != 0:
                    import warnings
                    warnings.warn("EpetraExt.Add returned error code in __iadd__",
                                   UserWarning, stacklevel=2)
        return self

   
    # To add two things while modifying neither, both must be FillCompleted
    def _add(self, other, sign = 1):

        if not self._getMatrix().Filled():
            self._getMatrix().FillComplete()
            
        if not other._getMatrix().Filled():
            other._getMatrix().FillComplete()
        
        # make the one with more nonzeros the right-hand operand
        # so addition is likely to succeed
        if self._getMatrix().NumGlobalNonzeros() > other._getMatrix().NumGlobalNonzeros():
            tempMatrix = self.copy()
            tempMatrix.__iadd__(other*sign)
        else:
            tempMatrix = other.copy()
            tempMatrix.__iadd__(self*sign)
            
        return tempMatrix

    def __add__(self, other):
        """
        Add two sparse matrices. The nonempty spots of one of them must be a 
        subset of the nonempty spots of the other one.
        
            >>> L = _TrilinosMatrix(size = 3)
            >>> L.addAt((3.,10.,numerix.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> L.addAt([0,0,0], [0,1,2], [0,1,2])
            >>> print L + _TrilinosIdentityMatrix(3)
             1.000000  10.000000   3.000000  
                ---     4.141593      ---    
             2.500000      ---     1.000000  
             
            >>> print L + 0
                ---    10.000000   3.000000  
                ---     3.141593      ---    
             2.500000      ---        ---    
            
            >>> print L + 3
            Traceback (most recent call last):
            ...
            AttributeError: 'int' object has no attribute '_getMatrix'
        """

        if other is 0:
            return self
        else:
            return self._add(other)
        
    def __sub__(self, other):
        if other is 0:
            return self
        else:
            return self._add(other, sign=-1)

    def __mul__(self, other):
        """
        Multiply a sparse matrix by another sparse matrix.
        
            >>> L1 = _TrilinosMatrix(size = 3)
            >>> L1.addAt((3,10,numerix.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> L2 = _TrilinosIdentityMatrix(size = 3)
            >>> L2.addAt((4.38,12357.2,1.1), (2,1,0), (1,0,2))
            
            >>> tmp = numerix.array(((1.23572000e+05, 2.31400000e+01, 3.00000000e+00),
            ...                      (3.88212887e+04, 3.14159265e+00, 0.00000000e+00),
            ...                      (2.50000000e+00, 0.00000000e+00, 2.75000000e+00)))

            >>> for i in range(0,3):
            ...     for j in range(0,3):
            ...         numerix.allclose(((L1*L2)[i,j],), tmp[i,j])
            True
            True
            True
            True
            True
            True
            True
            True
            True

        or a sparse matrix by a vector

            >>> tmp = numerix.array((29., 6.28318531, 2.5))       
            >>> numerix.allclose(L1 * numerix.array((1,2,3),'d'), tmp)
            1
            
        or a vector by a sparse matrix

            >>> tmp = numerix.array((7.5, 16.28318531,  3.))  
            >>> numerix.allclose(numerix.array((1,2,3),'d') * L1, tmp) 
            1

            
        """
        N = self._getMatrix().NumGlobalRows()

        if isinstance(other, _TrilinosMatrix):
            if isinstance(other._getMatrix(), Epetra.RowMatrix):
            
                if not self._getMatrix().Filled():
                    self._getMatrix().FillComplete()
                    
                if not other._getMatrix().Filled():
                    other._getMatrix().FillComplete()

                result = Epetra.CrsMatrix(Epetra.Copy, self.map, 0)

                EpetraExt.Multiply(self._getMatrix(), False, other._getMatrix(), False, result)
                return _TrilinosMatrix(matrix = result)
            else:
                raise TypeError
                
        else:
            shape = numerix.shape(other)
            if shape == ():
                result = self.copy()
                result._getMatrix().Scale(other)
                return result
            elif shape == (N,):

                if not self._getMatrix().Filled():
                    self._getMatrix().FillComplete()

                y = _numpyToTrilinosVector(other, self.map)
                result = Epetra.Vector(self.map)
                self._getMatrix().Multiply(False, y, result)
                return _trilinosToNumpyVector(result)
            else:
                raise TypeError
           
    def __rmul__(self, other):
        if type(numerix.ones(1)) == type(other):
            y = Epetra.Vector(other)
            result = Epetra.Vector(self.map)
            self._getMatrix().Multiply(True, y, result)
            return _trilinosToNumpyVector(result)
        else:
            return self * other
            
    def _getShape(self):
        N = self._getMatrix().NumGlobalRows()
        return (N,N)
        
    def put(self, vector, id1, id2):
        """
        Put elements of `vector` at positions of the matrix corresponding to (`id1`, `id2`)
        
            >>> L = _TrilinosMatrix(size = 3)
            >>> L.put((3.,10.,numerix.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> print L
                ---    10.000000   3.000000  
                ---     3.141593      ---    
             2.500000      ---        ---    
        """

        # Currently, all matrix building gets done on processor 0
        if(self.comm.MyPID() > 0):
            return

        if self._getMatrix().Filled():
            if self._getMatrix().ReplaceGlobalValues(id1, id2, vector) != 0:
                import warnings
                warnings.warn("ReplaceGlobalValues returned error code in put", 
                               UserWarning, stacklevel=2)
                # Possible different algorithm, to guarantee success:
                # 
                # Make a new matrix, 
                # Use addAt to put the values in it, 
                # Use replaceGlobalValues in the original matrix to zero out the terms 
                # And add the old one into the new one, 
                # Replace the old one.
                #
                # Would incur performance costs, and since FiPy does not use 
                # this function in such a way as would generate these errors,
                # I have not implemented the change.

        else:

            # This guarantees that it will actually replace the values that are there,
            # if there are any
            if self._getMatrix().NumGlobalNonzeros() == 0:
                self._getMatrix().InsertGlobalValues(id1, id2, vector)
            else:
                self._getMatrix().InsertGlobalValues(id1, id2, numerix.zeros(len(vector)))
                self._getMatrix().FillComplete()
                if self._getMatrix().ReplaceGlobalValues(id1, id2, vector) != 0:
                    import warnings
                    warnings.warn("ReplaceGlobalValues returned error code in put", 
                                   UserWarning, stacklevel=2)
                    # Possible different algorithm, to guarantee that it does not fail:
                    # 
                    # Make a new matrix, 
                    # Use addAt to put the values in it, 
                    # Use replaceGlobalValues in the original matrix to zero out the terms 
                    # And add the old one into the new one, 
                    # Replace the old one.
                    #
                    # Would incur performance costs, and since FiPy does not use 
                    # this function in such a way as would generate these errors,
                    # I have not implemented the change.
            
                             


    def putDiagonal(self, vector):
        """
        Put elements of `vector` along diagonal of matrix
        
            >>> L = _TrilinosMatrix(size = 3)
            >>> L.putDiagonal((3.,10.,numerix.pi))
            >>> print L
             3.000000      ---        ---    
                ---    10.000000      ---    
                ---        ---     3.141593  
            >>> L.putDiagonal((10.,3.))
            >>> print L
            10.000000      ---        ---    
                ---     3.000000      ---    
                ---        ---     3.141593  
        """
        
        
        if type(vector) in [type(1), type(1.)]:
            ids = numerix.arange(self._getMatrix().NumGlobalRows())
            tmp = numerix.zeros((self._getMatrix().NumGlobalRows), 'd')
            tmp[:] = vector
            if ids.dtype.name == 'int64':
                ids = ids.astype('int32')
            self.put(tmp, ids, ids)
        else:
            ids = numerix.arange(len(vector))
            if ids.dtype.name == 'int64':
                ids = ids.astype('int32')
            self.put(vector, ids, ids)

    def take(self, id1, id2):
        import warnings
        warnings.warn("""Trying to take from a Trilinos Matrix. That doesn't work.""",
                         UserWarning, stacklevel=2)
        raise TypeError

    def takeDiagonal(self):
        if not self._getMatrix().Filled():
            self._getMatrix().FillComplete()

        result = Epetra.Vector(self.map)
        self._getMatrix().ExtractDiagonalCopy(result)
        return _trilinosToNumpyVector(result)
    
    def addAt(self, vector, id1, id2):
        """
        Add elements of `vector` to the positions in the matrix corresponding to (`id1`,`id2`)
        
            >>> L = _TrilinosMatrix(size = 3)
            >>> L.addAt((3.,10.,numerix.pi,2.5), (0,0,1,2), (2,1,1,0))
            >>> L.addAt((1.73,2.2,8.4,3.9,1.23), (1,2,0,0,1), (2,2,0,0,2))
            >>> print L
            12.300000  10.000000   3.000000  
                ---     3.141593   2.960000  
             2.500000      ---     2.200000  
        """

        # Currently, all matrix building gets done on processor 0
        if(self.comm.MyPID() > 0):
            return

        ## This was added as it seems that trilinos does not like int64 arrays
        if hasattr(id1, 'astype') and id1.dtype.name == 'int64':
            id1 = id1.astype('int32')
        if hasattr(id2, 'astype') and id2.dtype.name == 'int64':
            id2 = id2.astype('int32')

        if not self._getMatrix().Filled():
            self._getMatrix().InsertGlobalValues(id1, id2, vector)
        else:
            if self._getMatrix().SumIntoGlobalValues(id1, id2, vector) != 0:
                import warnings
                warnings.warn("Summing into filled matrix returned error code",
                               UserWarning, stacklevel=2)
                # Possible change to this part of the code to do the following:
                #
                # Make a new matrix, 
                # Use addAt to put the values in it
                # Add the old one into the new one
                # Replace the old one. 
                #
                # Would incur performance costs, and since FiPy does not use 
                # this function in such a way as would generate these errors,
                # I have not implemented the change.


    def addAtDiagonal(self, vector):
        if type(vector) in [type(1), type(1.)]:
            ids = numerix.arange(self._getMatrix().GetGlobalRows())
            tmp = numerix.zeros((self._getMatrix().GetGlobalRows(),), 'd')
            tmp[:] = vector
            self.addAt(tmp, ids, ids)
        else:
            ids = numerix.arange(len(vector))
            self.addAt(vector, ids, ids)

    def exportMmf(self, filename):
        """
        Exports the matrix to a Matrix Market file of the given filename.
        """
        self.matrix.GlobalAssemble()
        self.matrix.FillComplete()
        EpetraExt.RowMatrixToMatrixMarketFile(filename, self.matrix)

    def getNumpyArray(self):
        raise NotImplemented

    def _getDistributedMatrix(self):
        """
        Returns an equivalent Trilinos matrix, but redistributed evenly over
        all processors.
        """
        if self.comm.NumProc() == 1:
            return self.matrix 
            # No redistribution necessary in serial mode
        else:
##            self.matrix.GlobalAssemble()
            totalElements = self.matrix.NumGlobalRows()

            DistributedMap = Epetra.Map(totalElements, 0, self.comm)
            RootToDist = Epetra.Import(DistributedMap, self.map)

            DistMatrix = Epetra.CrsMatrix(Epetra.Copy, DistributedMap, self.bandwidth*3/2)

            DistMatrix.Import(self.matrix, RootToDist, Epetra.Insert)

            return DistMatrix

def _numpyToTrilinosVector(v, map):
    """
    Takes a numpy vector and return an equivalent Trilinos vector, distributed
    across all processors as specified by the map.
    """
    if(map.Comm().NumProc() == 1):
        return Epetra.Vector(v)
        # No redistribution necessary in serial mode
    else:
        if map.Comm().MyPID() == 0:
            myElements=len(v)
        else:
            myElements=0
        RootMap = Epetra.Map(-1, range(0, myElements), 0, map.Comm())

        RootToDist = Epetra.Import(map, RootMap)

        rootVector = Epetra.Vector(RootMap, v)
        distVector = Epetra.Vector(map)
        distVector.Import(rootVector, RootToDist, Epetra.Insert)
        return distVector

def _trilinosToNumpyVector(v):
    """
    Takes a distributed Trilinos vector and gives all processors a copy of it
    in a numpy vector.
    """

    if(v.Comm().NumProc() == 1):
        return numerix.array(v)
    else:
        PersonalMap = Epetra.Map(-1, range(0, v.GlobalLength()), 0, v.Comm())
        DistToPers = Epetra.Import(PersonalMap, v.Map())

        PersonalV = Epetra.Vector(PersonalMap)
        PersonalV.Import(v, DistToPers, Epetra.Insert) 

        return numerix.array(PersonalV)
        
class _TrilinosIdentityMatrix(_TrilinosMatrix):
    """
    Represents a sparse identity matrix for Trilinos.
    """
    def __init__(self, size):
        """
        Create a sparse matrix with '1' in the diagonal
        
            >>> print _TrilinosIdentityMatrix(size = 3)
             1.000000      ---        ---    
                ---     1.000000      ---    
                ---        ---     1.000000  
        """
        _TrilinosMatrix.__init__(self, size = size, bandwidth = 1)
        ids = numerix.arange(size)
        self.addAt(numerix.ones(size), ids, ids)
        
def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__": 
    _test() 

