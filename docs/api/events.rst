.. currentmodule:: mafic

Events
======

Classes
-------

.. attributetable:: WebSocketClosedEvent

.. autoclass:: WebSocketClosedEvent

.. attributetable:: TrackStartEvent

.. autoclass:: TrackStartEvent

.. attributetable:: TrackEndEvent

.. autoclass:: TrackEndEvent

.. attributetable:: TrackExceptionEvent

.. autoclass:: TrackExceptionEvent

.. attributetable:: TrackStuckEvent

.. autoclass:: TrackStuckEvent

Callbacks
---------

.. function:: on_websocket_closed()

   Called when the websocket connection from Lavalink is closed to Discord.

   :param event: The event that was dispatched.
   :type event: :class:`WebSocketClosedEvent`

.. function:: on_track_start()

   Called when a track starts playing.

   :param event: The event that was dispatched.
   :type event: :class:`TrackStartEvent`

.. function:: on_track_end()

   Called when a track ends.

   :param event: The event that was dispatched.
   :type event: :class:`TrackEndEvent`

.. function:: on_track_exception()

   Called when a track throws an exception.

   :param event: The event that was dispatched.
   :type event: :class:`TrackExceptionEvent`

.. function:: on_track_stuck()

   Called when a track gets stuck.

   :param event: The event that was dispatched.
   :type event: :class:`TrackStuckEvent`

.. function:: on_node_stats()

   Called when Lavalink sends node statistics.

   .. versionadded:: 2.5

   :param node: The node that sent the statistics.
   :type node: :class:`Node`
