from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import random


class ConvexHull:
	def __init__(self, leftNode, rightNode):
		self.__leftNode = leftNode
		self.__rightNode = rightNode

	def getLeftNode(self):
		return self.__leftNode
	
	def getRightNode(self):
		return self.__rightNode
	
	def setLeftNode(self, node):
		self.__leftNode = node

	def setRightNode(self, node):
		self.__rightNode = node

class LinkedListNode:
	def __init__(self, coordinate, pointsTo):
		self._pointsTo = pointsTo
		self._coordinate = coordinate

	def getCoordinates(self):
		return self._coordinate
	
	def getXCoordinate(self):
		return self._coordinate.x()
	
	def getYCoordinate(self):
		return self._coordinate.y()
	
	def getPointsTo(self):
		return self._pointsTo
	
	def setPointTo(self, node):
		self._pointsTo = node

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):


# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

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

	def cHullSolver(self, points: list) -> ConvexHull:
		if len(points) < 4:
			return self.createSmallHull(points)
		else:
			leftHull: ConvexHull = self.cHullSolver(points[:len(points)//2])
			rightHull: ConvexHull = self.cHullSolver(points[len(points)//2:])
			return self.mergeHulls(leftHull, rightHull)

	# this is the smallest hull with only 2-3 points
	def createSmallHull(self, points: list) -> ConvexHull:
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
			rightNode = self.getRightNode(highNode, lowNode)

		return ConvexHull(leftNode, rightNode)
	
	def getRightNode(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode):
		if nodeOne.getXCoordinate() > nodeTwo.getXCoordinate():
			return nodeOne
		else:
			return nodeTwo

	
	def getHighAndLowPoint(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode) -> tuple[LinkedListNode, LinkedListNode]:
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
			newleftTopNode, negChanged = self.getMostNegativeSlope(currRightTopNode, currLeftTopNode)
			currLeftTopNode = newleftTopNode
			newRightTopNode, posChanged = self.getMostPositiveSlope(currLeftTopNode, currRightTopNode)
			currRightTopNode = newRightTopNode
			changed = negChanged or posChanged

		return currLeftTopNode, currRightTopNode

	def getLowerTangent(self, leftHull: ConvexHull, rightHull: ConvexHull) -> tuple[LinkedListNode, LinkedListNode]:
		currLeftLowerNode: LinkedListNode = leftHull.getRightNode()
		currRightLowerNode: LinkedListNode = rightHull.getLeftNode()

		changed = True
		while changed:
			newLeftLowerNode, posChanged = self.getMostPositiveSlope(currRightLowerNode, currLeftLowerNode)
			currLeftLowerNode = newLeftLowerNode
			newRightLowerNode, negChanged = self.getMostNegativeSlope(currLeftLowerNode, currRightLowerNode)
			currRightLowerNode = newRightLowerNode
			changed = negChanged or posChanged

		return currRightLowerNode, currLeftLowerNode

	def getMostNegativeSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode) -> tuple[LinkedListNode, bool]:
		startNode: LinkedListNode = movingNode
		currLowSlope: float = self.getSlope(movingNode, staticNode)
		lowNode: LinkedListNode = movingNode
		changed = False

		nextNode: LinkedListNode = movingNode.getPointsTo()
		while nextNode != startNode:
			thisSlope = self.getSlope(nextNode, staticNode)
			if thisSlope < currLowSlope:
				currLowSlope = thisSlope
				lowNode = nextNode
				changed = True
			nextNode = nextNode.getPointsTo()
			
		return lowNode, changed
	
	def getMostPositiveSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode) -> tuple[LinkedListNode, bool]:
		startNode: LinkedListNode = movingNode
		currHighSlope: float = self.getSlope(staticNode, movingNode)
		highNode: LinkedListNode = movingNode
		changed = False

		nextNode: LinkedListNode = movingNode.getPointsTo()
		while nextNode != startNode:
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

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		points.sort(key=lambda coordinate: coordinate.x()) # this is O(nlogn), google it
		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		hull = []
		convexHull: ConvexHull = self.cHullSolver(points)
		firstNode: LinkedListNode = convexHull.getLeftNode()
		hull.append(QLineF(firstNode.getCoordinates(), firstNode.getPointsTo().getCoordinates()) )
		nextNode: LinkedListNode = firstNode.getPointsTo()
		while nextNode != firstNode:
			hull.append(QLineF(nextNode.getCoordinates(), nextNode.getPointsTo().getCoordinates()))
			nextNode = nextNode.getPointsTo()
		t4 = time.time()
		polygon = hull
		QLineF()
		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))


# points = [QPointF(-0.8767629708201634, -0.15212788177681702), QPointF(-0.18302434877670737, 0.8413304625129518), QPointF(0.7844295680226157, 0.5386439713131719)]

# ConvexHullSolver.cHullSolver(points)