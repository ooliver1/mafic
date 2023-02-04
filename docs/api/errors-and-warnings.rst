.. currentmodule:: mafic

Errors and Warnings
===================

Errors
------

.. exception_hierarchy::

   - :exc:`Exception`
      - :exc:`MaficException`
         - :exc:`LibraryCompatibilityError`
            - :exc:`NoCompatibleLibraries`
            - :exc:`MultipleCompatibleLibraries`
         - :exc:`PlayerException`
            - :exc:`TrackLoadException`
            - :exc:`PlayerNotConnected`
         - :exc:`NodeAlreadyConnected`
         - :exc:`NoNodesAvailable`
         - :exc:`HTTPException`
            - :exc:`HTTPBadRequest`
            - :exc:`HTTPUnauthorized`
            - :exc:`HTTPNotFound`


.. autoexception:: MaficException

.. autoexception:: LibraryCompatibilityError

.. autoexception:: NoCompatibleLibraries

.. autoexception:: MultipleCompatibleLibraries

.. autoexception:: PlayerException

.. autoexception:: TrackLoadException
   :exclude-members: from_data

.. autoexception:: PlayerNotConnected

.. autoexception:: NoNodesAvailable

.. autoexception:: NodeAlreadyConnected

.. autoexception:: HTTPException

.. autoexception:: HTTPBadRequest

.. autoexception:: HTTPUnauthorized

.. autoexception:: HTTPNotFound

Warnings
--------

.. autoclass:: UnsupportedVersionWarning
