from enum import IntEnum


class Publisher:
    def __init__(self):
        self._eventDict = {}

    def _addListener(self, listener, eventName):
        eventKey = eventName
        if eventKey not in self._eventDict:
            self._eventDict[eventKey] = []
        self._eventDict[eventKey].append(listener)

    def _removeListener(self, listener, eventName):
        eventKey = eventName
        if eventKey in self._eventDict:
            if self._eventDict[eventKey].count(listener) > 0:
                self._eventDict[eventKey].remove(listener)

    def notify(self, eventName, eventContent):
        if eventName not in self._eventDict:
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


class eventName(IntEnum):
    MusicCompletation = 1
    MusicAdded = 2
    MusicDeleted = 3
    CursesKeyUp = 4
    CursesKeyDown = 5