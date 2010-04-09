#!/usr/bin/env python

## 
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "tools.py"
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

"""Vector utility functions that are inexplicably absent from Numeric
"""

from fipy.tools import numerix

def _putAddPy(vector, ids, additionVector, mask = False):
    additionVector = numerix.array(additionVector)

    if numerix.sometrue(mask):
        if len(vector.shape) < len(additionVector.shape):
            for j in range(vector.shape[0]):
                for id, value, masked in zip(ids.flat, additionVector[j].flat, mask.flat):
                    if not masked:
                        vector[j].flat[id] += value
        else:
            for id, value, masked in zip(ids.flat, additionVector.flat, mask.flat):
                if not masked:
                    vector.flat[id] += value

    else:
        if len(vector.shape) < len(additionVector.shape):
            for j in range(vector.shape[0]):
                for id, value in zip(ids.flat, additionVector[j].flat):
                    vector[j].flat[id] += value
        else:
            for id, value in zip(ids.flat, additionVector.flat):
                vector.flat[id] += value

## FIXME: inline version doesn't account for all of the conditions that Python 
## version does.
def _putAddIn(vector, ids, additionVector):
    from fipy.tools import inline
    inline._runInline("""
        int ID = ids[i];
	vector[ID] += additionVector[i];
    """,
    vector=vector, ids=ids, additionVector=numerix.array(additionVector),
    ni = len(ids.flat))

def putAdd(vector, ids, additionVector):
    """ This is a temporary replacement for Numeric.put as it was not doing
    what we thought it was doing.
    """
    from fipy.tools import inline
    inline._optionalInline(_putAddIn, _putAddPy, vector, ids, additionVector)

def prune(array, shift, start=0, axis=0):
    """
    removes elements with indices i = start + shift * n
    where n = 0, 1, 2, ...

        >>> prune(numerix.arange(10), 3, 5)
        array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        >>> prune(numerix.arange(10), 3, 2)
        array([0, 1, 3, 4, 6, 7, 9])
        >>> prune(numerix.arange(10), 3)
        array([1, 2, 4, 5, 7, 8])
        >>> prune(numerix.arange(4, 7), 3)
        array([5, 6])

    """

    takeArray = numerix.nonzero(numerix.arange(array.shape[-1]) % shift != start)[0]
    return numerix.take(array, takeArray, axis=axis)

def _test(): 
    import doctest
    return doctest.testmod()
    
if __name__ == "__main__":
    _test() 
