========
Overview
========

.. only:: latex

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
   specific problems.  Our approach, combining the FV method and :term:`Python`,
   provides a tool that is extensible, powerful and freely available. A
   significant advantage to :term:`Python` is the existing suite of tools for
   array calculations, sparse matrices and data rendering. 

   The :term:`FiPy` framework includes terms for transient diffusion,
   convection and standard sources, enabling the solution of arbitrary
   combinations of coupled elliptic, hyperbolic and parabolic PDEs. Currently
   implemented models include phase field
   [BoettingerReview:2002]_ [ChenReview:2002]_ [McFaddenReview:2002]_ treatments of
   polycrystalline, dendritic, and electrochemical phase transformations as
   well as a level set treatment of the electrodeposition process
   [NIST:damascene:2001]_.

.. only:: latex
  
   The latest information about :term:`FiPy` can be found at
   http://www.ctcms.nist.gov/fipy/.

---------------------------------
Even if you don't read manuals...
---------------------------------

...please read :ref:`INSTALLATION` and the :ref:`FAQ`. 

--------------------------------
What's new in version |release|?
--------------------------------

The relatively small change in version number belies significant advances
in :term:`FiPy` capabilities. This release did not receive a "full" version
increment because it is completely (er... [#almost]_) compatible with older scripts.

The significant changes since version 2.0.2 are:

- :term:`FiPy` can use :term:`Trilinos` for `solving in parallel`_.

- We have switched from :term:`MayaVi` 1 to :term:`Mayavi` 2. This 
  :class:`~fipy.viewers.viewer.Viewer` is an independent process that 
  allows interaction with the display while a simulation is running.

- Documentation has been switched to :term:`Sphinx`, allowing the entire manual to 
  be available on the web and for our documentation to link to the
  documentation for packages such as :mod:`numpy`, :mod:`scipy`,
  :mod:`matplotlib`, and for :term:`Python` itself.

Tickets fixed in this release::

    171	update the mayavi viewer to use  mayavi 2
    286	'matplotlib: list index out of range' when no title given, but only sometimes
    197	~binOp doesn't work on branches/version-2_0
    194	`easy_install` instructions for MacOSX are broken
    192	broken setuptools url with python 2.6
    184	The FiPy webpage seems to be broken on Internet Explorer
    168	Switch documentation to use `:math:` directive
    198	FiPy2.0.2 LinearJORSolver.__init__  calls Solver rather than PysparseSolver
    199	`gmshExport.exportAsMesh()` doesn't work
    195	broken arithmetic face to cell distance calculations

.. warning::

   :term:`FiPy` 2 brought unavoidable syntax changes from :term:`FiPy` 1.
   Please see :mod:`examples.updating.update1_0to2_0` for guidance on the
   changes that you will need to make to your :term:`FiPy` 1.x scripts.
   Few, if any, changes should be needed to migrate from :term:`FiPy` 2.0.x
   to :term:`FiPy` 2.1.

-------------------------
Download and Installation
-------------------------

Please refer to :ref:`INSTALLATION` for details on download and
installation. :term:`FiPy` can be redistributed and/or modified
freely, provided that any derivative works bear some notice that they
are derived from it, and any modified versions bear some notice that
they have been modified.

-------
Support
-------

You can communicate with the :term:`FiPy` developers and with other users via our
`mailing list`_ and we welcome you to use the `tracking
system`_ for bugs, support requests, feature requests and
patch submissions <http://matforge.org/fipy/report>. We welcome collaborative efforts on this project.

:term:`FiPy` is a member of MatForge_, a project of the `Materials Digital Library
Pathway`_. This National Science Foundation funded service provides
management of our public source code repository, our bug tracking system, and
a "wiki" space for public contributions of code snippets, discussions, and
tutorials.

.. toctree::

   documentation/MAIL

------------------------
Conventions and Notation
------------------------

:term:`FiPy` is driven by :term:`Python` script files than you can view or modify in any
text editor.  :term:`FiPy` sessions are invoked from a command-line shell, such
as :command:`tcsh` or :command:`bash`.

Throughout, text to be typed at the keyboard will appear ``like this``.
Commands to be issued from an interactive shell will appear::

    $ like this

where you would enter the text ("``like this``") following the shell prompt,
denoted by "``$``".

Text blocks of the form::

    >>> a = 3 * 4
    >>> a
    12
    >>> if a == 12:
    ...     print "a is twelve"
    ...
    a is twelve

are intended to indicate an interactive session in the :term:`Python` interpreter.
We will refer to these as "interactive sessions" or as "doctest blocks".
The text "``>>>``" at the beginning of a line denotes the *primary prompt*,
calling for input of a :term:`Python` command.  The text "``...``" denotes the
*secondary prompt*, which calls for input that continues from the line
above, when required by :term:`Python` syntax.  All remaining lines, which begin
at the left margin, denote output from the :term:`Python` interpreter.  In all
cases, the prompt is supplied by the :term:`Python` interpreter and should not be
typed by you.

.. warning::

   :term:`Python` is sensitive to indentation and care should be taken to enter
   text exactly as it appears in the examples.

When references are made to file system paths, it is assumed that the
current working directory is the :term:`FiPy` distribution directory, refered to
as the "base directory", such that::

    examples/diffusion/steadyState/mesh1D.py

will correspond to, *e.g.*::

    /some/where/FiPy-X.Y/examples/diffusion/steadyState/mesh1D.py

Paths will always be rendered using POSIX conventions (path elements
separated by "``/``").  Any references of the form::

    examples.diffusion.steadyState.mesh1D

are in the :term:`Python` module notation and correspond to the equivalent POSIX
path given above.

We may at times use a 

.. note::

   to indicate something that may be of interest

or a

.. warning::

   to indicate something that could cause serious problems.

.. _PARALLEL:

-------------------
Solving in Parallel
-------------------

:term:`FiPy` can use :term:`Trilinos` to solve equations in parallel, as 
long as they are defined on a "``Grid``" mesh 
(:class:`~fipy.meshes.numMesh.grid1D.Grid1D`, 
:class:`~fipy.meshes.numMesh.cylindricalGrid1D.CylindricalGrid1D`,
:class:`~fipy.meshes.numMesh.grid2D.Grid2D`,
:class:`~fipy.meshes.numMesh.cylindricalGrid2D.CylindricalGrid2D`, or
:class:`~fipy.meshes.numMesh.grid3D.Grid3D`). 

.. attention::

   :term:`Trilinos` *must* be compiled with MPI support.

.. note::

   A design wart presently *also* requires that :term:`PySparse` be
   installed. We hope to alleviate this requirement in a future release.

* It should not generally be necessary to change anything in your script. s
  Simply invoke::

     $ mpirun -np {# of processors} python myScript.py

  instead of::

     $ python myScript.py

A complete list of the changes to FiPy's examples needed for parallel 
can be found at

  http://www.matforge.org/fipy/wiki/upgrade2_0examplesTo2_1

Most of the changes were required to ensure that :term:`FiPy` provides the
same literal output for both single and multiple processor solutions and
are not relevant to most "real" scripts. The two changes you *might* wish
to make to your own scripts are:

 * It is now preferable to use the 
   :class:`~fipy.solvers.DefaultAssymetricSolver` instead of the 
   :class:`~fipy.solvers.linearLUSolver.LinearLUSolver`. 

 * When solving in parallel, :term:`FiPy` essentially breaks the problem up 
   into separate sub-domains and solves them (somewhat) independently. 
   :term:`FiPy` generally "does the right thing", but if you find that you 
   need to do something with the entire solution, you can call
   ``var.``:meth:`~fipy.variables.cellVariable.CellVariable.getGlobalValue`.

.. [#almost] Only two examples from :term:`FiPy` 2.0 fail when run with :term:`FiPy` 2.1:

    * :mod:`examples.phase.symmetry` fails because 
      :class:`~fipy.meshes.numMesh.mesh.Mesh` no longer provides a
      :meth:`~fipy.meshes.numMesh.mesh.Mesh.getCells` method. The mechanism
      for enforcing symmetry in the updated example is both clearer and 
      faster.

    * :mod:`examples.levelSet.distanceFunction.circle` fails because of a 
      change in the comparison of masked values.

   Both of these are subtle issues unlikely to affect very many 
   :term:`FiPy` users.

.. _MSEL:                 http://www.msel.nist.gov/
.. _CTCMS:                http://www.ctcms.nist.gov/
.. _Metallurgy Division:  http://www.metallurgy.nist.gov/
.. _NIST:                 http://www.nist.gov/
.. _Subversion:           http://www.nist.gov/cgi-bin/exit_nist.cgi?url=http://matforge.org/fipy/browser
.. _compressed archive:   http://www.ctcms.nist.gov/fipy/download/FiPy-1.1.tar.gz
.. _tracking system:      http://www.nist.gov/cgi-bin/exit_nist.cgi?url=http://matforge.org/fipy/report
.. _mailing list:         http://www.ctcms.nist.gov/fipy/mail.html
.. _Sourceforge:          http://www.nist.gov/cgi-bin/exit_nist.cgi?url=http://www.sourceforge.net/projects/fipy
.. _Materials Digital Library Pathway: http://www.nist.gov/cgi-bin/exit_nist.cgi?url=http://matdl.org
.. _MatForge:             http://www.nist.gov/cgi-bin/exit_nist.cgi?url=http://matforge.org/
