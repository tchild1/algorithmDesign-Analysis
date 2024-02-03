from LinkedListNodeClass import LinkedListNode 

class ConvexHull:
	def __init__(self, leftNode: LinkedListNode, rightNode: LinkedListNode):
		self.__leftNode = leftNode
		self.__rightNode = rightNode

	def getLeftNode(self) -> LinkedListNode:
		return self.__leftNode
	
	def getRightNode(self) -> LinkedListNode:
		return self.__rightNode
	
	def setLeftNode(self, node: LinkedListNode) -> None:
		self.__leftNode = node

	def setRightNode(self, node: LinkedListNode) -> None:
		self.__rightNode = node
