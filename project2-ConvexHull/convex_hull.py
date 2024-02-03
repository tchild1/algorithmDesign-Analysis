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
RED = (255,0,0)


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
			return self.twoPointsToHull(points)
		else:
			return self.threePointsToHull(points)
	
	def twoPointsToHull(self, points: List[QPointF]) -> ConvexHull:
		leftNode: LinkedListNode = LinkedListNode(points[0], None, None)
		rightNode: LinkedListNode = LinkedListNode(points[1], None, None)
		leftNode.setPointTo(rightNode)
		rightNode.setPointTo(leftNode)
		
		return ConvexHull(leftNode, rightNode)
	
	def threePointsToHull(self, points: List[QPointF]) -> ConvexHull:
		highPoint, lowPoint = self.getHighAndLowPoint(points[1], points[2])
		leftNode: LinkedListNode = LinkedListNode(points[0], None, None)
		highNode: LinkedListNode = LinkedListNode(highPoint, None, None)
		lowNode: LinkedListNode = LinkedListNode(lowPoint, None, None)
		if self.isClockwise(leftNode, highNode, lowNode):
			leftNode.setPointTo(highNode)
			highNode.setPointTo(lowNode)
			lowNode.setPointTo(leftNode)
		else:
			highNode.setPointTo(leftNode)
			lowNode.setPointTo(highNode)
			leftNode.setPointTo(lowNode)

		rightNode: LinkedListNode = self.getRightmostNode(highNode, lowNode)
		return ConvexHull(leftNode, rightNode)

	def isClockwise(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode, nodeThree: LinkedListNode) -> bool:
		nodeOneTwoSlope = self.getSlope(nodeOne, nodeTwo)
		nodeTwoThreeSlope = self.getSlope(nodeTwo, nodeThree)
		nodeThreeOneSlope = self.getSlope(nodeThree, nodeOne)
		if nodeOneTwoSlope <= nodeTwoThreeSlope < nodeThreeOneSlope or nodeTwoThreeSlope < nodeThreeOneSlope <= nodeOneTwoSlope or nodeThreeOneSlope <= nodeOneTwoSlope < nodeTwoThreeSlope:
			return True
		else:
			return False
	
	def getRightmostNode(self, nodeOne: LinkedListNode, nodeTwo: LinkedListNode) -> LinkedListNode:
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
			currLeftTopNode, negChanged = self.getMostNegativeSlope(currRightTopNode, currLeftTopNode, False)
			currRightTopNode, posChanged = self.getMostPositiveSlope(currLeftTopNode, currRightTopNode, True)
			changed = negChanged or posChanged

		return currLeftTopNode, currRightTopNode

	def getLowerTangent(self, leftHull: ConvexHull, rightHull: ConvexHull) -> tuple[LinkedListNode, LinkedListNode]:
		currLeftLowerNode: LinkedListNode = leftHull.getRightNode()
		currRightLowerNode: LinkedListNode = rightHull.getLeftNode()

		changed = True
		while changed:
			currLeftLowerNode, posChanged = self.getMostPositiveSlope(currRightLowerNode, currLeftLowerNode, True)
			currRightLowerNode, negChanged = self.getMostNegativeSlope(currLeftLowerNode, currRightLowerNode, False)
			changed = negChanged or posChanged

		return currRightLowerNode, currLeftLowerNode

	def getMostNegativeSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode, clockwise: bool) -> tuple[LinkedListNode, bool]:
		currLowSlope: float = self.getSlope(movingNode, staticNode)
		lowNode: LinkedListNode = movingNode
		changed = False

		if clockwise:
			while True:
				nextNode: LinkedListNode = movingNode.getPointsTo()
				nextNodeSlope = self.getSlope(nextNode, staticNode)
				if nextNodeSlope < currLowSlope:
					currLowSlope = nextNodeSlope
					lowNode = nextNode
					changed = True
					nextNode = nextNode.getPointsTo()
				else:
					break
		else:
			while True:
				nextNode: LinkedListNode = movingNode.getPointsFrom()
				nextNodeSlope = self.getSlope(nextNode, staticNode)
				if nextNodeSlope < currLowSlope:
					currLowSlope = nextNodeSlope
					lowNode = nextNode
					changed = True
					nextNode = nextNode.getPointsFrom()
				else:
					break

		return lowNode, changed
	
	def getMostPositiveSlope(self, staticNode: LinkedListNode, movingNode: LinkedListNode, clockwise: bool) -> tuple[LinkedListNode, bool]:
		currHighSlope: float = self.getSlope(staticNode, movingNode)
		highNode: LinkedListNode = movingNode
		changed = False

		if clockwise:
			while True:
				nextNode: LinkedListNode = movingNode.getPointsTo()
				nextNodeSlope = self.getSlope(staticNode, nextNode)
				if nextNodeSlope > currHighSlope:
					currHighSlope = nextNodeSlope
					highNode = nextNode
					changed = True
					nextNode = nextNode.getPointsTo()
				else:
					break
		else:
			while True:
				nextNode: LinkedListNode = movingNode.getPointsFrom()
				nextNodeSlope = self.getSlope(staticNode, nextNode)
				if nextNodeSlope > currHighSlope:
					currHighSlope = nextNodeSlope
					highNode = nextNode
					changed = True
					nextNode = nextNode.getPointsFrom()
				else:
					break
			
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

		t3 = time.time()
		convexHull: ConvexHull = self.cHullSolver(points)
		polygon: List[QLineF] = self.getPolygon(convexHull)
		t4 = time.time()

		self.showHull(polygon, RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def getPolygon(self, convexHull: ConvexHull) -> List[QLineF]:
		hull: List[QLineF] = []
		hullSet: set = set()

		firstNode: LinkedListNode = convexHull.getLeftNode()
		hullSet.add(firstNode)
		hull.append(QLineF(firstNode.getCoordinates(), firstNode.getPointsTo().getCoordinates()))
		nextNode: LinkedListNode = firstNode.getPointsTo()

		while nextNode not in hullSet:
			hullSet.add(nextNode)
			hull.append(QLineF(nextNode.getCoordinates(), nextNode.getPointsTo().getCoordinates()))
			nextNode = nextNode.getPointsTo()

		return hull


# ptList = [QPointF(-0.5953131868542136, 0.48545400641747793), 
# 		  QPointF(-0.5277211083630247, 0.36785735549528353), 
# 		  QPointF(-0.49516410074486683, 0.6170161121201718), 
# 		  QPointF(-0.4593888800452677, -0.015017353252701815), 
# 		  QPointF(-0.34562136924110765, -0.10332775188642507), 
# 		  QPointF(0.01778358411153924, 0.4931237651687721), 
# 		  QPointF(0.11971653895701584, -0.9471886651325723), 
# 		  QPointF(0.39558727064418875, -0.37503109712505367), 
# 		  QPointF(0.4769690522174861, 0.8408775138127984), 
# 		  QPointF(0.49912591211496893, -0.03502892198634444)
# 		  ]

# cHullSolver = ConvexHullSolver()

# cHullSolver.compute_hull(ptList)
