class Publisher:
    def __init__(self):
        self._listeners = []
        self._eventDict = {}

    def _addListener(self, listener, eventName):
        if self._listeners.count(listener) < 1:
            self._listeners.append(listener)
        if eventName not in self._eventDict:
            self._eventDict[eventName] = []
        self._eventDict[eventName].append(listener)

    def _removeListener(self, listener, event):
        self._listeners.remove(listener)
        for eventKey in self._eventDict:
            for _listener in eventKey:
                if _listener == listener:
                    eventKey.pop(listener)

    def notify(self, eventName, eventContent):
        if eventName not in self._eventDict:
            return
        if not self._listeners or len(self._listeners) <= 0:
            return
        event = Event(eventName, eventContent)
        for listener in self._eventDict[eventName]:
            if isinstance(listener, Listener):
                listener.onNotify(event)


class Listener:
    def onNotify(self, event):
        pass

    def addObserver(self, publisher, eventName):
        if not isinstance(publisher, Publisher):
            return False
        publisher._addListener(self, eventName)
        return True

    def removeObserver(self, publisher, eventName):
        if not isinstance(publisher, Publisher):
            return False
        publisher._removeListener(self, eventName)
        return True


class Event:
    def __init__(self, eventName, eventContent):
        self.eventName = eventName
        self.eventContent = eventContent