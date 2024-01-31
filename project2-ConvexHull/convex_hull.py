from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
# elif PYQT_VER == 'PYQT4':
# 	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
from LinkedListNodeClass import LinkedListNode 
from ConvexHullClass import ConvexHull
from typing import List

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

class ConvexHullSolver(QObject):

	def __init__( self):
		super().__init__()
		self.pause = False

	# Helper methods to interact with the GUI
	
	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

	# Hull solver main function and helper functions

	def cHullSolver(self, points: List[QPointF]) -> ConvexHull:
		if len(points) < 4:
			return self.createSmallHull(points)
		else:
			leftHull: ConvexHull = self.cHullSolver(points[:len(points)//2])
			rightHull: ConvexHull = self.cHullSolver(points[len(points)//2:])
			return self.mergeHulls(leftHull, rightHull)

	# this is the smallest hull with only 2-3 points
	def createSmallHull(self, points: List[QPointF]) -> ConvexHull:
		if len(points) == 2:
			leftNode: LinkedListNode = LinkedListNode(points[0], None)
			rightNode: LinkedListNode = LinkedListNode(points[1], None)
			leftNode.setPointTo(rightNode)
			rightNode.setPointTo(leftNode)
		else:
			highPoint, lowPoint = self.getHighAndLowPoint(points[1], points[2])
			leftNode: LinkedListNode = LinkedListNode(points[0], None)
			highNode: LinkedListNode = LinkedListNode(highPoint, None)
			lowNode: LinkedListNode = LinkedListNode(lowPoint, None)
			leftNode.setPointTo(highNode)
			highNode.setPointTo(lowNode)
			lowNode.setPointTo(leftNode)
			rightNode: LinkedListNode = self.getRightNode(highNode, lowNode)

		return ConvexHull(leftNode, rightNode)
	
	def getRightNode(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode) -> LinkedListNode:
		if nodeOne.getXCoordinate() > nodeTwo.getXCoordinate():
			return nodeOne
		else:
			return nodeTwo

	
	def getHighAndLowPoint(self, nodeOne: QPointF, nodeTwo: QPointF) -> tuple[QPointF, QPointF]:
		if nodeOne.y() > nodeTwo.y():
			return nodeOne, nodeTwo
		else:
			return nodeTwo, nodeOne
		
	def mergeHulls(self, leftHull: ConvexHull, rightHull: ConvexHull) -> ConvexHull:
		leftHullTopNode, rightHullTopNode = self.getTopTangent(leftHull, rightHull)
		rightHullBottomNode, leftHullBottomNode = self.getLowerTangent(leftHull, rightHull)
		leftHullTopNode.setPointTo(rightHullTopNode)
		rightHullBottomNode.setPointTo(leftHullBottomNode)
		return ConvexHull(leftHull.getLeftNode(), rightHull.getRightNode())

	def getTopTangent(self, leftHull: ConvexHull, rightHull: ConvexHull) -> tuple[LinkedListNode, LinkedListNode]:
		currLeftTopNode: LinkedListNode = leftHull.getRightNode()
		currRightTopNode: LinkedListNode = rightHull.getLeftNode()

		changed = True
		while changed:
			currLeftTopNode, negChanged = self.getMostNegativeSlope(currRightTopNode, currLeftTopNode)
			currRightTopNode, posChanged = self.getMostPositiveSlope(currLeftTopNode, currRightTopNode)
			changed = negChanged or posChanged

		return currLeftTopNode, currRightTopNode

	def getLowerTangent(self, leftHull: ConvexHull, rightHull: ConvexHull) -> tuple[LinkedListNode, LinkedListNode]:
		currLeftLowerNode: LinkedListNode = leftHull.getRightNode()
		currRightLowerNode: LinkedListNode = rightHull.getLeftNode()

		changed = True
		while changed:
			currLeftLowerNode, posChanged = self.getMostPositiveSlope(currRightLowerNode, currLeftLowerNode)
			currRightLowerNode, negChanged = self.getMostNegativeSlope(currLeftLowerNode, currRightLowerNode)
			changed = negChanged or posChanged

		return currRightLowerNode, currLeftLowerNode

	def getMostNegativeSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode) -> tuple[LinkedListNode, bool]:
		visitedNodes: set[LinkedListNode] = set() # IM using a set here because checking if the nodes were equal to the starting node caused an infinite loop... is this ok? I did the same on positive
		visitedNodes.add(movingNode)
		currLowSlope: float = self.getSlope(movingNode, staticNode)
		lowNode: LinkedListNode = movingNode
		changed = False

		nextNode: LinkedListNode = movingNode.getPointsTo()
		while nextNode not in visitedNodes:
			visitedNodes.add(nextNode)
			thisSlope = self.getSlope(nextNode, staticNode)
			if thisSlope < currLowSlope:
				currLowSlope = thisSlope
				lowNode = nextNode
				changed = True
			nextNode = nextNode.getPointsTo()
			
		return lowNode, changed
	
	def getMostPositiveSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode) -> tuple[LinkedListNode, bool]:
		visitedNodes: set[LinkedListNode] = set()
		visitedNodes.add(movingNode)
		currHighSlope: float = self.getSlope(staticNode, movingNode)
		highNode: LinkedListNode = movingNode
		changed = False

		nextNode: LinkedListNode = movingNode.getPointsTo()
		while nextNode not in visitedNodes:
			visitedNodes.add(nextNode)
			thisSlope = self.getSlope(staticNode, nextNode)
			if thisSlope > currHighSlope:
				currHighSlope = thisSlope
				highNode = nextNode
				changed = True
			nextNode = nextNode.getPointsTo()

		return highNode, changed

	def getSlope(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode) -> float:
		rise = nodeOne.getYCoordinate() - nodeTwo.getYCoordinate()
		run = nodeOne.getXCoordinate() - nodeTwo.getXCoordinate()

		return rise/run

	# Called by GUI to compute Hull
	def compute_hull(self, points: List[QPointF], pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		points = sorted(points, key=lambda coordinate: coordinate.x())
		t2 = time.time()
		print(t1-t2)

		t3 = time.time()
		convexHull: ConvexHull = self.cHullSolver(points)
		polygon: List[QLineF] = self.getPolygon(convexHull)
		t4 = time.time()

		RED = (255,0,0)
		self.showHull(polygon, RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def getPolygon(self, convexHull: ConvexHull) -> List[QLineF]:
		hull: List[QLineF] = []

		firstNode: LinkedListNode = convexHull.getLeftNode()
		hull.append(QLineF(firstNode.getCoordinates(), firstNode.getPointsTo().getCoordinates()))
		nextNode: LinkedListNode = firstNode.getPointsTo()

		while nextNode != firstNode:
			hull.append(QLineF(nextNode.getCoordinates(), nextNode.getPointsTo().getCoordinates()))
			nextNode = nextNode.getPointsTo()

		return hull
