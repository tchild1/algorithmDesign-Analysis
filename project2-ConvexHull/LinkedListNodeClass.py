from PyQt6.QtCore import QLineF, QPointF, QObject


class LinkedListNode:
	def __init__(self, coordinate, pointsTo):
		self._pointsTo = pointsTo
		self._coordinate = coordinate

	def getCoordinates(self) -> QPointF:
		return self._coordinate
	
	def getXCoordinate(self) -> float:
		return self._coordinate.x()
	
	def getYCoordinate(self) -> float:
		return self._coordinate.y()
	
	def getPointsTo(self) -> 'LinkedListNode':
		return self._pointsTo
	
	def setPointTo(self, node) -> None:
		self._pointsTo = node