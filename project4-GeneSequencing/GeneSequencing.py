#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import random
from nodeClass import Node

# Used to compute the bandwidth for banded version
BAND = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass

# This is the method called by the GUI. _seq1_ and _seq2_ are two sequences to be aligned, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

	def align(self, seq1: str, seq2: str, banded: bool, align_length: int):
		self.banded: bool = banded
		self.MaxCharactersToAlign: int = align_length

		if banded:
			z = self.alignBanded(seq1, seq2, align_length)
			y = z[0]
			x = z[1]
			v = z[2]
		else:
			z = self.alignUnbanded(seq1, seq2, align_length+1)
			y = z[0]
			x = z[1]
			v = z[2]


###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
		score = y
		alignment1 = x
		alignment2 = v
###################################################################################################

		return {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
	
	def alignBanded(self, seq1, seq2, alignLength) -> tuple[int, str, str]:
		dpBoundedArray: list[list[Node]] = self.initBoundedArrayAndBaseCases(seq1, seq2, alignLength+1)

		for row in range(1, min(len(dpBoundedArray), alignLength+1)):
			for col in range(0, min(len(dpBoundedArray[row]), alignLength+1)):
				self.calculateValueBanded(dpBoundedArray, row, col, seq1, seq2, alignLength)

		minVal = float('inf')
		for col in range(min(len(dpBoundedArray[row]), alignLength+1)-1, -1, -1):
			if dpBoundedArray[min(len(dpBoundedArray)-1, alignLength)][col].getScore() != None:
				if dpBoundedArray[min(len(dpBoundedArray)-1, alignLength)][col].getScore() < minVal:
					minVal = dpBoundedArray[min(len(dpBoundedArray)-1, alignLength)][col].getScore()
					minCell = dpBoundedArray[min(len(dpBoundedArray)-1, alignLength)][col]
		
		return (minVal, '', '')


	def calculateValueBanded(self, dpBoundedArray: list[list[Node]], row: int, col: int, seq1: str, seq2: str, alignLength):
		if self.alreadyHasValue(dpBoundedArray, row, col):
			pass
		else:
			if self.isInFirstBandedRows(row):
				if self.isInBand(row, col):
					if self.isAMatch(row, col, seq1, seq2):
						if self.isRightMostCellInBand(row, col):
							scoreSet = {
								'match': dpBoundedArray[row-1][col-1].getScore() + MATCH,
								'sub': dpBoundedArray[row-1][col-1].getScore() + SUB,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
						else:
							scoreSet = {
								'match': dpBoundedArray[row-1][col-1].getScore() + MATCH,
								'sub': dpBoundedArray[row-1][col-1].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col].getScore() + INDEL,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
					else:
						if self.isRightMostCellInBand(row, col):
							scoreSet = {
								'sub': dpBoundedArray[row-1][col-1].getScore() + SUB,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
						else:
							scoreSet = {
								'sub': dpBoundedArray[row-1][col-1].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col].getScore() + INDEL,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}


					minScore = scoreSet.get('sub', float('inf'))
					dpBoundedArray[row][col].setScore(scoreSet['sub'])
					dpBoundedArray[row][col].setBackPointer(row-1, col)
					if scoreSet.get('indelUp', float('inf')) < minScore:
						minScore = scoreSet.get('indelUp', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['indelUp'])
						dpBoundedArray[row][col].setBackPointer(row-1, col+1)
					if scoreSet.get('indelLeft', float('inf')) < minScore:
						minScore = scoreSet.get('indelLeft', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['indelLeft'])
						dpBoundedArray[row][col].setBackPointer(row, col-1)
					if scoreSet.get('match', float('inf')) < minScore:
						minScore = scoreSet.get('match', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['match'])
						dpBoundedArray[row][col].setBackPointer(row-1, col)

			else:
				if self.isInWord((col + (row - BAND)), seq1, alignLength):
					if self.isAMatch((col + (row - BAND)), row, seq1, seq2):
						if self.isLeftMostCell(col):
							scoreSet = {
								'match': dpBoundedArray[row-1][col].getScore() + MATCH,
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col+1].getScore() + INDEL,
							}
						elif self.isRightMostCell(col):
							scoreSet = {
								'match': dpBoundedArray[row-1][col].getScore() + MATCH,
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
						else:
							scoreSet = {
								'match': dpBoundedArray[row-1][col].getScore() + MATCH,
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col+1].getScore() + INDEL,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
					else:
						if self.isLeftMostCell(col):
							scoreSet = {
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col+1].getScore() + INDEL,
							}
						elif self.isRightMostCell(col):
							scoreSet = {
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}
						else:
							scoreSet = {
								'sub': dpBoundedArray[row-1][col].getScore() + SUB,
								'indelUp': dpBoundedArray[row-1][col+1].getScore() + INDEL,
								'indelLeft': dpBoundedArray[row][col-1].getScore() + INDEL
							}

					minScore = scoreSet.get('sub', float('inf'))
					dpBoundedArray[row][col].setScore(scoreSet['sub'])
					dpBoundedArray[row][col].setBackPointer(row-1, col)
					if scoreSet.get('indelUp', float('inf')) < minScore:
						minScore = scoreSet.get('indelUp', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['indelUp'])
						dpBoundedArray[row][col].setBackPointer(row-1, col+1)
					if scoreSet.get('indelLeft', float('inf')) < minScore:
						minScore = scoreSet.get('indelLeft', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['indelLeft'])
						dpBoundedArray[row][col].setBackPointer(row, col-1)
					if scoreSet.get('match', float('inf')) < minScore:
						minScore = scoreSet.get('match', float('inf'))
						dpBoundedArray[row][col].setScore(scoreSet['match'])
						dpBoundedArray[row][col].setBackPointer(row-1, col)

	def isLeftMostCell(self, col: int):
		return col == 0
	
	def isInWord(self, col: int, seq1: str, alignLength):
		return col < min(len(seq1)+1, alignLength+1)
	
	def isRightMostCellInBand(self, row: int, col: int):
		return col == (((BAND * 2) + 1) - (BAND - row) - 1)
	
	def isLeftMostCellInBand(self, row: int, col: int):
		return col == 0
	
	def isRightMostCell(self, col: int):
		return col == (BAND * 2)

	def isInFirstBandedRows(self, row: int):
		return row <= BAND
	
	def isInLastBandedRows(self, row: int, dpBoundedArray: list[list[Node]]):
		return row > len(dpBoundedArray) - BAND -1
	
	def isInBand(self, row: int, col: int):
		return (col < ((BAND * 2) + 1) - (BAND - row))

	def alreadyHasValue(self, dpBoundedArray: list[list[Node]], row: int, col: int):
		return dpBoundedArray[row][col].getScore() != None


	def alignUnbanded(self, seq1: str, seq2: str, alignLength: int) -> tuple[int, str, str]:
		dpArray: list[list[Node]] = self.initializeArrayAndBaseCases(seq1, seq2, alignLength)

		for row in range(1, min(len(dpArray), alignLength)):
			for col in range(1, min(len(dpArray[row]), alignLength)):
				self.calculateValue(row, col, seq1, seq2, dpArray)

		if abs(len(seq1)-len(seq2)) > 7:
			return (float('inf'), '', '')
		# retString = self.getAlignment(dpArray, len(dpArray)-1, len(dpArray[row])-1, False, seq1, seq2)

		return (dpArray[len(dpArray)-1][len(dpArray[row])-1].getScore(), '', '')

	def initBoundedArrayAndBaseCases(self, seq1: str, seq2: str, alignLength: int):
		dpArray: list[list[Node]] = [[Node() for letter2 in range(min(alignLength, (BAND*2)+1))] for letter1 in range(min(alignLength, len(seq2)+1))]
		
		# init base cases
		val = 0
		for cell in range(BAND + 1):
			dpArray[cell][0].setScore(val)
			val += INDEL

		val = 0
		for cell in range(BAND + 1):
			dpArray[0][cell].setScore(val)
			val += INDEL
		
		return dpArray

	def calculateValue(self, row: int, col: int, seq1: str, seq2: str, dpArray: list[list[Node]]):
		if self.isAMatch(row, col, seq1, seq2):
			scoreSet = {
				'match': dpArray[row-1][col-1].getScore() + MATCH,
				'sub': dpArray[row-1][col-1].getScore() + SUB,
				'indelUp': dpArray[row-1][col].getScore() + INDEL,
				'indelLeft': dpArray[row][col-1].getScore() + INDEL
			}
		else:
			scoreSet = {
				'sub': dpArray[row-1][col-1].getScore() + SUB,
				'indelUp': dpArray[row-1][col].getScore() + INDEL,
				'indelLeft': dpArray[row][col-1].getScore() + INDEL
			}

		minKey = min(scoreSet, key=lambda k: scoreSet[k])
		if minKey == 'match':
			dpArray[row][col].setScore(scoreSet['match'])
			dpArray[row][col].setBackPointer(row-1, col-1)
		elif minKey == 'sub':
			dpArray[row][col].setScore(scoreSet['sub'])
			dpArray[row][col].setBackPointer(row-1, col-1)
		elif minKey == 'indelUp':
			dpArray[row][col].setScore(scoreSet['indelUp'])
			dpArray[row][col].setBackPointer(row-1, col)
		elif minKey == 'indelLeft':
			dpArray[row][col].setScore(scoreSet['indelLeft'])
			dpArray[row][col].setBackPointer(row, col-1)


	def isAMatch(self, row: int , col: int, seq1: str, seq2: str) -> bool:
		if len(seq2) < col or len(seq1) < row:
			return False
		return seq2[col-1] == seq1[row-1]


	def initializeArrayAndBaseCases(self, seq1: str, seq2: str, alignLength: int) -> list[list[Node]]:
		# create array
		dpArray = [[Node() for letter2 in range(min(alignLength, len(seq2)+1))] for letter1 in range(min(alignLength, len(seq1)+1))]

		# init base cases
		val = 0
		for cell in range(len(dpArray)):
			dpArray[cell][0].setScore(val)
			val += INDEL

		val = 0
		for cell in range(len(dpArray[0])):
			dpArray[0][cell].setScore(val)
			val += INDEL
		
		return dpArray


	def getAlignment(self, dpArray: list[list[Node]], row: int, col: int, banded: bool, seq1: str, seq2: str):
		if banded:
			pass
		else:

			retString: str = ''

			while row != 0 and col != 0:

				endNode = dpArray[row][col]
				backRow = endNode.getBackPointer()[0]
				backCol = endNode.getBackPointer()[1]

				rowDiff = row - backRow
				colDiff = col - backCol


				if (rowDiff == 1) and (colDiff == 1) and self.isAMatch(row, col, seq1, seq2):
					retString = seq1[row-1] + retString
				elif (rowDiff == 1) and (colDiff == 1):
					retString = seq1[row-1] + retString
				elif (rowDiff == 0) and (colDiff == 1):
					retString = '-' + retString
				elif (rowDiff == 1) and (colDiff == 0):
					retString = '-' + retString

				row = backRow
				col = backCol

			return retString
