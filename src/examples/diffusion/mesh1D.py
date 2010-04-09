#!/usr/bin/env python

## 
 # ###################################################################
 #  FiPy - Python-based finite volume PDE solver
 # 
 #  FILE: "mesh1D.py"
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

r"""
To run this example from the base :term:`FiPy` directory, type::
    
    $ examples/diffusion/mesh1D.py
    
at the command line. Different stages of the example should be displayed,
along with prompting messages in the terminal.

This example takes the user through assembling a simple problem with :term:`FiPy`.
It describes different approaches to a 1D diffusion problem with constant
diffusivity and fixed value boundary conditions such that,

.. math::
   :label: eq:diffusion:mesh1D:constantD
   
   \frac{\partial \phi}{\partial t} = D \nabla^2 \phi.

The first step is to define a one dimensional domain with 50 solution
points. The :class:`~fipy.meshes.numMesh.grid1D.Grid1D` object represents a linear structured grid. The
parameter ``dx`` refers to the grid spacing (set to unity here).

>>> from fipy import *

>>> nx = 50
>>> dx = 1.
>>> mesh = Grid1D(nx = nx, dx = dx)

:term:`FiPy` solves all equations at the centers of the cells of the mesh. We
thus need a :class:`~fipy.variables.cellVariable.CellVariable` object to hold the values of the
solution, with the initial condition :math:`\phi = 0` at :math:`t = 0`, 

>>> phi = CellVariable(name="solution variable", 
...                    mesh=mesh,
...                    value=0.)

We'll let

>>> D = 1.

for now. 

The set of boundary conditions are given to the equation as a Python
:keyword:`tuple` or :keyword:`list` (the distinction is not generally important to :term:`FiPy`).
The boundary conditions 

.. math::

   \phi =
   \begin{cases}
       0& \text{at \(x = 1\),} \\
       1& \text{at \(x = 0\).}
   \end{cases}

are formed with a value 

>>> valueLeft = 1
>>> valueRight = 0

and a set of faces over which they apply.

.. note::
    
   Only faces around the exterior of the mesh can be used for boundary
   conditions.

For example, here the exterior faces on the left of the domain are
extracted by ``mesh``:meth:`~fipy.meshes.common.mesh.Mesh.getFacesLeft``. A :class:`~fipy.boundaryConditions.fixedValue.FixedValue` boundary condition is
created with these faces and a value (``valueLeft``). 

>>> BCs = (FixedValue(faces=mesh.getFacesRight(), value=valueRight),
...        FixedValue(faces=mesh.getFacesLeft(), value=valueLeft))

.. note::
    
   If no boundary conditions are specified on exterior faces, the default
   boundary condition is ``FixedFlux(faces=someFaces, value=0.)``, equivalent to
   :math:`\vec{n} \cdot \nabla \phi \rvert_\text{someFaces} = 0`.

If you have ever tried to numerically solve
Eq. :eq:`eq:diffusion:mesh1D:constantD`, 
you most likely attempted "explicit finite differencing" with code
something like::
    
    for step in range(steps):
        for j in range(cells):
            phi_new[j] = phi_old[j] \
              + (D * dt / dx**2) * (phi_old[j+1] - 2 * phi_old[j] + phi_old[j-1])
        time += dt
        
plus additional code for the boundary conditions. In :term:`FiPy`, you would write

.. index:: ExplicitDiffusionTerm, TransientTerm

>>> eqX = TransientTerm() == ExplicitDiffusionTerm(coeff=D)

The largest stable timestep that can be taken for this explicit 1D
diffusion problem is :math:`\Delta t \le \Delta x^2 / (2 D)`.
   
We limit our steps to 90% of that value for good measure

>>> timeStepDuration = 0.9 * dx**2 / (2 * D)
>>> steps = 100

If we're running interactively, we'll want to view the result, but not if
this example is being run automatically as a test. We accomplish this by
having Python check if this script is the "``__main__``" script, which will
only be true if we explicitly launched it and not if it has been imported
by another script such as the automatic tester. The factory function
:func:`Viewer` returns a suitable viewer depending on available
viewers and the dimension of the mesh.

.. index::
   module: fipy.viewers

>>> phiAnalytical = CellVariable(name="analytical value",
...                              mesh=mesh)

>>> if __name__ == '__main__':
...     viewer = Viewer(vars=(phi, phiAnalytical),
...                     datamin=0., datamax=1.)
...     viewer.plot()

In a semi-infinite domain, the analytical solution for this transient
diffusion problem is given by
:math:`\phi = 1 - \erf(x/2\sqrt{D t})`. If the :term:`SciPy` library is available,
the result is tested against the expected profile: 

>>> x = mesh.getCellCenters()[0]
>>> t = timeStepDuration * steps

>>> try:
...     from scipy.special import erf
...     phiAnalytical.setValue(1 - erf(x / (2 * sqrt(D * t))))
... except ImportError:
...     print "The SciPy library is not available to test the solution to \
... the transient diffusion equation"

We then solve the equation by repeatedly looping in time:

>>> for step in range(steps):
...     eqX.solve(var=phi,
...               boundaryConditions=BCs,
...               dt=timeStepDuration)
...     if __name__ == '__main__':
...         viewer.plot()

>>> print phi.allclose(phiAnalytical, atol = 7e-4)
1

>>> if __name__ == '__main__':
...     raw_input("Explicit transient diffusion. Press <return> to proceed...")

.. image:: mesh1Dexplicit.*
   :width: 90%
   :align: center

-----

Although explicit finite differences are easy to program, we have just seen
that this 1D transient diffusion problem is limited to taking rather small
time steps. If, instead, we represent 
Eq. :eq:`eq:diffusion:mesh1D:constantD` 
as::

    phi_new[j] = phi_old[j] \
      + (D * dt / dx**2) * (phi_new[j+1] - 2 * phi_new[j] + phi_new[j-1])
    
it is possible to take much larger time steps. Because ``phi_new`` appears on
both the left and right sides of the equation, this form is called
"implicit". In general, the "implicit" representation is much more
difficult to program than the "explicit" form that we just used, but in
:term:`FiPy`, all that is needed is to write

>>> eqI = TransientTerm() == DiffusionTerm(coeff=D)

reset the problem

>>> phi.setValue(valueRight)

and rerun with much larger time steps

>>> timeStepDuration *= 10
>>> steps /= 10
>>> for step in range(steps):
...     eqI.solve(var=phi,
...               boundaryConditions=BCs,
...               dt=timeStepDuration)
...     if __name__ == '__main__':
...         viewer.plot()

>>> print phi.allclose(phiAnalytical, atol = 2e-2)
1

>>> if __name__ == '__main__':
...     raw_input("Implicit transient diffusion. Press <return> to proceed...")

.. image:: mesh1Dimplicit.*
   :width: 90%
   :align: center

Note that although much larger *stable* timesteps can be taken with this
implicit version (there is, in fact, no limit to how large an implicit
timestep you can take for this particular problem), the solution is less
*accurate*. One way to achieve a compromise between *stability* and
*accuracy* is with the Crank-Nicholson scheme, represented by::
    
    phi_new[j] = phi_old[j] + (D * dt / (2 * dx**2)) * \
                    ((phi_new[j+1] - 2 * phi_new[j] + phi_new[j-1])
                     + (phi_old[j+1] - 2 * phi_old[j] + phi_old[j-1]))
    
which is essentially an average of the explicit and implicit schemes from
above. This can be rendered in :term:`FiPy` as easily as

>>> eqCN = eqX + eqI

We again reset the problem

>>> phi.setValue(valueRight)

and apply the Crank-Nicholson scheme until the end, when we apply one step
of the fully implicit scheme to drive down the error
(see, *e.g.*, section 19.2 of [NumericalRecipes]_).

>>> for step in range(steps - 1):
...     eqCN.solve(var=phi,
...                boundaryConditions=BCs,
...                dt=timeStepDuration)
...     if __name__ == '__main__':
...         viewer.plot()
>>> eqI.solve(var=phi,
...           boundaryConditions=BCs,
...           dt=timeStepDuration)
>>> if __name__ == '__main__':
...     viewer.plot()

>>> print phi.allclose(phiAnalytical, atol = 3e-3)
1

>>> if __name__ == '__main__':
...     raw_input("Crank-Nicholson transient diffusion. Press <return> to proceed...")

-----

As mentioned above, there is no stable limit to how large a time step can
be taken for the implicit diffusion problem. In fact, if the time evolution
of the problem is not interesting, it is possible to eliminate the time
step altogether by omitting the :class:`~fipy.terms.transientTerm.TransientTerm`. The steady-state diffusion
equation

.. math::

   D \nabla^2 \phi = 0

is represented in :term:`FiPy` by

>>> DiffusionTerm(coeff=D).solve(var=phi,
...                              boundaryConditions=BCs)
...                                      

>>> if __name__ == '__main__':
...     viewer.plot()

The analytical solution to the steady-state problem is no longer an error
function, but simply a straight line, which we can confirm to a tolerance
of :math:`10^{-10}`.

>>> L = nx * dx
>>> print phi.allclose(valueLeft + (valueRight - valueLeft) * x / L, 
...                    rtol = 1e-10, atol = 1e-10)
1

>>> if __name__ == '__main__':
...     raw_input("Implicit steady-state diffusion. Press <return> to proceed...")

.. image:: mesh1DsteadyState.*
   :width: 90%
   :align: center
       
------

Often, boundary conditions may be functions of another variable in the
system or of time.

For example, to have

.. math::
    
   \phi = \begin{cases}
       (1 + \sin t) / 2 &\text{on \( x = 0 \)} \\
       0 &\text{on \( x = L \)} \\
   \end{cases}

we will need to declare time :math:`t` as a :class:`~fipy.variables.variable.Variable`

>>> time = Variable()

and then declare our boundary condition as a function of this :class:`~fipy.variables.variable.Variable`

>>> BCs = (FixedValue(faces=mesh.getFacesLeft(), value=0.5 * (1 + sin(time))),
...        FixedValue(faces=mesh.getFacesRight(), value=0.))

When we update ``time`` at each timestep, the left-hand boundary
condition will automatically update,

>>> dt = .1
>>> while time() < 15:
...     time.setValue(time() + dt)
...     eqI.solve(var=phi, dt=dt, boundaryConditions=BCs)
...     if __name__ == '__main__':
...         viewer.plot()

>>> if __name__ == '__main__':
...     raw_input("Time-dependent boundary condition. Press <return> to proceed...")

.. image:: mesh1DtimedBC.*
   :width: 90%
   :align: center

------

Many interesting problems do not have simple, uniform diffusivities. We consider a
steady-state diffusion problem  

.. math::

   \nabla \cdot ( D \nabla \phi) = 0,

with a spatially varying diffusion coefficient

.. math::

   D = \begin{cases}
   1& \text{for \( 0 < x < L / 4 \),} \\
   0.1& \text{for \( L / 4 \le x < 3 L / 4 \),} \\
   1& \text{for \( 3 L / 4 \le x < L \),}
   \end{cases}

and with boundary conditions
:math:`\phi = 0` at :math:`x = 0` and :math:`D \frac{\partial \phi}{\partial x}
= 1` at :math:`x = L`, where :math:`L` is the length of the solution
domain. Exact numerical answers to this problem are found when the mesh
has cell centers that lie at :math:`L / 4` and :math:`3 L / 4`, or when the
number of cells in the mesh :math:`N_i` satisfies :math:`N_i = 4 i + 2`,
where :math:`i` is an integer. The mesh we've been using thus far is
satisfactory, with :math:`N_i = 50` and :math:`i = 12`.
   
Because :term:`FiPy` considers diffusion to be a flux from one :class:`~fipy.meshes.numMesh.cell.Cell` to the next,
through the intervening :class:`~fipy.meshes.numMesh.face.Face`, we must define the non-uniform diffusion
coefficient on the mesh faces

.. index:: FaceVariable

>>> D = FaceVariable(mesh=mesh, value=1.0)
>>> x = mesh.getFaceCenters()[0]
>>> D.setValue(0.1, where=(L / 4. <= x) & (x < 3. * L / 4.))

The boundary conditions are a fixed value of 

>>> valueLeft = 0.

to the left and a fixed flux of

>>> fluxRight = 1.
    
to the right:

.. index:: FixedFlux

>>> BCs = (FixedValue(faces=mesh.getFacesLeft(), value=valueLeft),
...        FixedFlux(faces=mesh.getFacesRight(), value=fluxRight))

We re-initialize the solution variable
    
>>> phi.setValue(0)
    
and obtain the steady-state solution with one implicit solution step

>>> DiffusionTerm(coeff = D).solve(var=phi, 
...                                boundaryConditions = BCs)

The analytical solution is simply

.. math::
    
   \phi = \begin{cases}
   x & \text{for \( 0 < x < L/4 \),} \\
   10 x - 9L/4 & \text{for \( L/4 \le x < 3 L / 4 \),} \\
   x + 18 L / 4 & \text{for \( 3 L / 4 \le x < L \),}
   \end{cases}
   
or

>>> x = mesh.getCellCenters()[0]
>>> phiAnalytical.setValue(x)
>>> phiAnalytical.setValue(10 * x - 9. * L / 4. , 
...                        where=(L / 4. <= x) & (x < 3. * L / 4.))
>>> phiAnalytical.setValue(x + 18. * L / 4. , 
...                        where=3. * L / 4. <= x)
>>> print phi.allclose(phiAnalytical, atol = 1e-8, rtol = 1e-8)
1

And finally, we can plot the result

>>> if __name__ == '__main__':
...     Viewer(vars=(phi, phiAnalytical)).plot()
...     raw_input("Non-uniform steady-state diffusion. Press <return> to proceed...")


.. image:: mesh1Dnon-uniform.*
   :width: 90%
   :align: center

------

Often, the diffusivity is not only non-uniform, but also depends on
the value of the variable, such that

.. math::
   :label: eq:diffusion:mesh1D:variableD

   \frac{\partial \phi}{\partial t} = \nabla \cdot [ D(\phi) \nabla \phi].
    
With such a non-linearity, it is generally necessary to "sweep" the
solution to convergence. This means that each time step should be
calculated over and over, using the result of the previous sweep to update
the coefficients of the equation, without advancing in time. In :term:`FiPy`, this
is accomplished by creating a solution variable that explicitly retains its
"old" value by specifying ``hasOld`` when you create it. The variable does
not move forward in time until it is explicity told to ``updateOld()``. In
order to compare the effects of different numbers of sweeps, let us create
a list of variables: ``phi[0]`` will be the variable that is actually being
solved and ``phi[1]`` through ``phi[4]`` will display the result of taking the
corresponding number of sweeps (``phi[1]`` being equivalent to not sweeping
at all).

>>> valueLeft = 1.
>>> valueRight = 0.
>>> phi = [
...     CellVariable(name="solution variable",
...                  mesh=mesh,
...                  value=valueRight,
...                  hasOld=1),
...     CellVariable(name="1 sweep",
...                  mesh=mesh),
...     CellVariable(name="2 sweeps",
...                  mesh=mesh),
...     CellVariable(name="3 sweeps",
...                  mesh=mesh),
...     CellVariable(name="4 sweeps",
...                  mesh=mesh)
... ]

If, for example,

.. math::

   D = D_0 (1 - \phi)
   
we would simply write
Eq. :eq:`eq:diffusion:mesh1D:variableD`   
as

>>> D0 = 1.
>>> eq = TransientTerm() == DiffusionTerm(coeff=D0 * (1 - phi[0]))

.. note::
    
   Because of the non-linearity, the Crank-Nicholson scheme does not work
   for this problem.
   
We apply the same boundary conditions that we used for the uniform
diffusivity cases

>>> BCs = (FixedValue(faces=mesh.getFacesRight(), value=valueRight),
...        FixedValue(faces=mesh.getFacesLeft(), value=valueLeft))

Although this problem does not have an exact transient solution, it
can be solved in steady-state, with

.. math::

   \phi(x) = 1 - \sqrt{\frac{x}{L}}

>>> x = mesh.getCellCenters()[0]
>>> phiAnalytical.setValue(1. - sqrt(x/L))

We create a viewer to compare the different numbers of sweeps with the
analytical solution from before.

>>> if __name__ == '__main__':
...     viewer = Viewer(vars=phi + [phiAnalytical],
...                     datamin=0., datamax=1.)
...     viewer.plot()

As described above, an inner "sweep" loop is generally required for
the solution of non-linear or multiple equation sets. Often a
conditional is required to exit this "sweep" loop given some
convergence criteria. Instead of using the :meth:`solve` method equation,
when sweeping, it is often useful to call :meth:`sweep` instead. The
:meth:`sweep` method behaves the same way as :meth:`solve`, but returns the
residual that can then be used as part of the exit condition.

We now repeatedly run the problem with increasing numbers of
sweeps.

>>> for sweeps in range(1,5):
...     phi[0].setValue(valueRight)
...     for step in range(steps):
...         # only move forward in time once per time step
...         phi[0].updateOld()
...         
...         # but "sweep" many times per time step
...         for sweep in range(sweeps):
...             res = eq.sweep(var=phi[0],
...                            boundaryConditions=BCs,
...                            dt=timeStepDuration)
...         if __name__ == '__main__':
...             viewer.plot()
...             
...     # copy the final result into the appropriate display variable
...     phi[sweeps].setValue(phi[0])
...     if __name__ == '__main__':
...         viewer.plot()
...         raw_input("Implicit variable diffusity. %d sweep(s). \
... Residual = %f. Press <return> to proceed..." % (sweeps, (abs(res))))

As can be seen, sweeping does not dramatically change the result, but the
"residual" of the equation (a measure of how accurately it has been solved)
drops about an order of magnitude with each additional sweep. 

.. attention::
    
   Choosing an optimal balance between the number of time steps, the number
   of sweeps, the number of solver iterations, and the solver tolerance is
   more art than science and will require some experimentation on your part
   for each new problem.

Finally, we can increase the number of steps to approach equilibrium, or we
can just solve for it directly

>>> eq = DiffusionTerm(coeff=D0 * (1 - phi[0]))

>>> phi[0].setValue(valueRight)
>>> res = 1e+10
>>> while res > 1e-6:
...     res = eq.sweep(var=phi[0],
...                    boundaryConditions=BCs,
...                    dt=timeStepDuration)


>>> print phi[0].allclose(phiAnalytical, atol = 1e-1)
1

>>> if __name__ == '__main__':
...     viewer.plot()
...     raw_input("Implicit variable diffusity - steady-state. \
... Press <return> to proceed...")

.. image:: mesh1Dvariable.*
   :width: 90%
   :align: center

------

If this example had been written primarily as a script, instead of as
documentation, we would delete every line that does not begin with
either "``>>>``" or "``...``", and then delete those prefixes from the
remaining lines, leaving::
    
     #!/usr/bin/env python

     ## This script was derived from
     ## 'examples/diffusion/mesh1D.py'

     nx = 50
     dx = 1.
     mesh = Grid1D(nx = nx, dx = dx)
     phi = CellVariable(name="solution variable", 
                        mesh=mesh,
                        value=0)
  
::

     eq = DiffusionTerm(coeff=D0 * (1 - phi[0]))
     phi[0].setValue(valueRight)
     res = 1e+10
     while res > 1e-6:
         res = eq.sweep(var=phi[0],
                        boundaryConditions=BCs,
                        dt=timeStepDuration)

     print phi[0].allclose(phiAnalytical, atol = 1e-1)
     # Expect:
     # 1
     # 
     if __name__ == '__main__':
         viewer.plot()
         raw_input("Implicit variable diffusity - steady-state. \
     Press <return> to proceed...")

Your own scripts will tend to look like this, although you can always write
them as doctest scripts if you choose.  You can obtain a plain script
like this from some `.../example.py` by typing::
    
    $ python setup.py copy_script --From .../example.py --To myExample.py

at the command line.

Most of the :term:`FiPy` examples will be a
mixture of plain scripts and doctest documentation/tests.

.. :term:`FiPy` replace:: `FiPy`
"""

__docformat__ = 'restructuredtext'

if __name__ == '__main__':
    import fipy.tests.doctestPlus
    exec(fipy.tests.doctestPlus._getScript())

