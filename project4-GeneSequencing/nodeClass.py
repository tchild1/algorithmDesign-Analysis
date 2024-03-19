class Node:
	def __init__(self) -> None:
		self._backPointer: tuple[int, int] = (None, None)
		self._score: int = None

	def setBackPointer(self, row: int, col: int) -> None:
		self._backPointer = (row, col)

	def setScore(self, score: int):
		self._score = score

	def getScore(self) -> int:
		return self._score
	
	def getBackPointer(self) -> tuple[int, int]:
		return self._backPointer
