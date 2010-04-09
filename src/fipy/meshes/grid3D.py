#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - Python-based phase field solver
 # 
 #  FILE: "grid3D.py"
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

from fipy.tools import parallel

def Grid3D(dx = 1., dy = 1., dz = 1., nx = None, ny = None, nz = None, overlap=2, parallelModule=parallel):
    from numMesh import uniformGrid3D
    from numMesh import grid3D

    from fipy.tools import numerix
    if numerix.getShape(dx) == () \
      and numerix.getShape(dy) == () \
      and numerix.getShape(dz) == ():
        if nx is None:
            nx = 1
        if ny is None:
            ny = 1
        if nz is None:
            nz = 1
        return uniformGrid3D.UniformGrid3D(dx = dx, dy = dy, dz = dz,
                                           nx = nx or 1, ny = ny or 1, nz = nz or 1,
                                           overlap=overlap, parallelModule=parallelModule)
    else:
        return grid3D.Grid3D(dx = dx, dy = dy, dz = dz, nx = nx, ny = ny, nz = nz,
                             overlap=overlap, parallelModule=parallelModule)
