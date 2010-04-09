"""
:term:`FiPy` is an object oriented, partial differential equation (PDE) solver,
written in :term:`Python`, based on a standard finite volume (FV)
approach.  The framework has been developed in the `Metallurgy Division`_
and Center for Theoretical and Computational Materials Science (CTCMS_), in
the Materials Science and Engineering Laboratory (MSEL_) at the National
Institute of Standards and Technology (NIST_).

The solution of coupled sets of PDEs is ubiquitous to the numerical
simulation of science problems.  Numerous PDE solvers exist, using a
variety of languages and numerical approaches. Many are proprietary,
expensive and difficult to customize.  As a result, scientists spend
considerable resources repeatedly developing limited tools for
specific problems.  Our approach, combining the FV method and Python_,
provides a tool that is extensible, powerful and freely available. A
significant advantage to Python_ is the existing suite of tools for
array calculations, sparse matrices and data rendering. 

The :term:`FiPy` framework includes terms for transient diffusion, convection and
standard sources, enabling the solution of arbitrary combinations of
coupled elliptic, hyperbolic and parabolic PDEs.  Currently implemented
models include phase field |citePhaseField| treatments of polycrystalline,
dendritic, and electrochemical phase transformations as well as a level set
treatment of the electrodeposition process |citeCEAC|.

.. _MSEL:                 http://www.msel.nist.gov/
.. _CTCMS:                http://www.ctcms.nist.gov/
.. _Metallurgy Division:  http://www.metallurgy.nist.gov/
.. _NIST:                 http://www.nist.gov/
"""
__docformat__ = 'restructuredtext'

from pkg_resources import get_distribution

FiPy = get_distribution(__name__)

__version__ = FiPy.version

from boundaryConditions import *
from meshes import *
from solvers import *
from steppers import *
from terms import *
from tools import *
from variables import *
from viewers import *
from models import *

try:
    from PyTrilinos import Epetra
    
    if Epetra.PyComm().NumProc() > 1:
        raw_input_original = raw_input
        def mpi_raw_input(prompt=""):
            import sys
            Epetra.PyComm().Barrier()
            sys.stdout.flush()
            if Epetra.PyComm().MyPID() == 0:
                sys.stdout.write(prompt)
                sys.stdout.flush()
                return sys.stdin.readline()
            else:
                return ""
        raw_input = mpi_raw_input

except ImportError:
    pass
