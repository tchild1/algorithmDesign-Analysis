from LinkedListNodeClass import LinkedListNode 

class ConvexHull:
	def __init__(self, leftNode, rightNode):
		self.__leftNode = leftNode
		self.__rightNode = rightNode

	def getLeftNode(self) -> LinkedListNode:
		return self.__leftNode
	
	def getRightNode(self) -> LinkedListNode:
		return self.__rightNode
	
	def setLeftNode(self, node) -> None:
		self.__leftNode = node

	def setRightNode(self, node) -> None:
		self.__rightNode = node
