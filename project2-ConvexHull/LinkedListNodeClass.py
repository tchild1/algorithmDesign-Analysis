from PyQt6.QtCore import QPointF

class LinkedListNode:
	def __init__(self, coordinate: QPointF, pointsTo: 'LinkedListNode', pointsFrom: 'LinkedListNode'):
		self._pointsTo = pointsTo
		self._pointsFrom = pointsFrom
		self._coordinate = coordinate

	def getCoordinates(self) -> QPointF:
		return self._coordinate
	
	def getXCoordinate(self) -> float:
		return self._coordinate.x()
	
	def getYCoordinate(self) -> float:
		return self._coordinate.y()
	
	def getPointsTo(self) -> 'LinkedListNode':
		return self._pointsTo
	
	def getPointsFrom(self) -> 'LinkedListNode':
		return self._pointsFrom
	
	def setPointFrom(self, node: 'LinkedListNode') -> None:
		self._pointsFrom = node
		node._setPointToPriv(self)
	
	def setPointTo(self, node: 'LinkedListNode') -> None:
		self._pointsTo = node
		node._setPointFromPriv(self)

	def _setPointFromPriv(self, node: 'LinkedListNode') -> None:
		self._pointsFrom = node
	
	def _setPointToPriv(self, node: 'LinkedListNode') -> None:
		self._pointsTo = node