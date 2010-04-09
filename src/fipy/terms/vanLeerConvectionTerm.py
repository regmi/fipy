#!/usr/bin/env python

## -*-Pyth-*-
 # ###################################################################
 #  FiPy - a finite volume PDE solver in Python
 # 
 #  FILE: "vanLeerConvectionTerm.py"
 #
 #  Author: Jonathan Guyer <guyer@nist.gov>
 #  Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #  Author: James Warren   <jwarren@nist.gov>
 #    mail: NIST
 #     www: http://www.ctcms.nist.gov/fipy/
 #  
 # ========================================================================
 # This document was prepared at the National Institute of Standards
 # and Technology by employees of the Federal Government in the course
 # of their official duties.  Pursuant to title 17 Section 105 of the
 # United States Code this document is not subject to copyright
 # protection and is in the public domain.  vanLeerConvectionTerm.py
 # is an experimental work.  NIST assumes no responsibility whatsoever
 # for its use by other parties, and makes no guarantees, expressed
 # or implied, about its quality, reliability, or any other characteristic.
 # We would appreciate acknowledgement if the document is used.
 # 
 # This document can be redistributed and/or modified freely
 # provided that any derivative works bear some notice that they are
 # derived from it, and any modified versions bear some notice that
 # they have been modified.
 # ========================================================================
 #  See the file "license.terms" for information on usage and  redistribution
 #  of this file, and for a DISCLAIMER OF ALL WARRANTIES.
 #  
 # ###################################################################
 ##

"""
"""

__docformat__ = 'restructuredtext'

from fipy.tools import numerix

from fipy.terms.explicitUpwindConvectionTerm import ExplicitUpwindConvectionTerm
from fipy.tools import numerix

class VanLeerConvectionTerm(ExplicitUpwindConvectionTerm):
    def _getGradient(self, normalGradient, gradUpwind):
        gradUpUpwind = -gradUpwind + 2 * normalGradient

        avg = 0.5 * (abs(gradUpwind) + abs(gradUpUpwind))
        min3 = numerix.minimum(numerix.minimum(abs(gradUpwind), abs(gradUpUpwind)), avg)

        grad = numerix.where(gradUpwind * gradUpUpwind < 0.,
                             0., 
                             numerix.where(gradUpUpwind > 0.,
                                           min3,
                                           -min3))

        return grad
        
    def _getOldAdjacentValues(self, oldArray, id1, id2, dt):
        oldArray1, oldArray2 = ExplicitUpwindConvectionTerm._getOldAdjacentValues(self, oldArray, id1, id2, dt)
        
        mesh = oldArray.getMesh()

        interiorIDs = numerix.nonzero(mesh.getInteriorFaces())[0]
        interiorFaceAreas = numerix.take(mesh._getFaceAreas(), interiorIDs)
        interiorFaceNormals = numerix.take(mesh._getOrientedFaceNormals(), interiorIDs, axis=-1)
        
        # Courant-Friedrichs-Levy number
        interiorCFL = abs(numerix.take(self._getGeomCoeff(mesh), interiorIDs)) * dt
        
        gradUpwind = (oldArray2 - oldArray1) / numerix.take(mesh._getCellDistances(), interiorIDs)
        
        vol1 = numerix.take(mesh.getCellVolumes(), id1)
        self.CFL = interiorCFL / vol1
        
        oldArray1 += 0.5 * self._getGradient(numerix.dot(numerix.take(oldArray.getGrad(), id1, axis=-1), interiorFaceNormals), gradUpwind) \
            * (vol1 - interiorCFL) / interiorFaceAreas

        vol2 = numerix.take(mesh.getCellVolumes(), id2)
        
        self.CFL = numerix.maximum(interiorCFL / vol2, self.CFL)

        oldArray2 += 0.5 * self._getGradient(numerix.dot(numerix.take(oldArray.getGrad(), id2, axis=-1), -interiorFaceNormals), -gradUpwind) \
            * (vol2 - interiorCFL) / interiorFaceAreas
        
        return oldArray1, oldArray2

    def _getFigureOfMerit(self):
        return min(0.2 / self.CFL)
