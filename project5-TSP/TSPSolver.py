#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import copy

class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None
		self.counter = 0
		self.bssf = {}
		self.maxPriorityQueueLen = 0
		self.pruned = 0
		self.numOfBSSFUpdates = 0
		self.numOfStatesCreated = 0

	def getCounter(self):
		self.counter += 1
		return self.counter

	def setupWithScenario(self, scenario: Scenario):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution,
		time spent to find solution, number of permutations tried during search, the
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def defaultRandomTour(self, time_allowance: float = 60.0):
		results: dict = {}
		cities: list[City] = self._scenario.getCities()
		ncities: int = len(cities)
		foundTour: bool = False
		count: int = 0
		bssf: TSPSolution = None
		start_time: time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route: list[City] = []
			# Now build the route using the random permutation
			for i in range(ncities):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def greedy(self, timeAllowance):
		# get all cities
		cities: list[City] = copy.deepcopy(self._scenario.getCities())
		tour: list[City] = []

		startTime: time = time.time()

		currCity: City = cities.pop(0)
		tour.append(currCity)

		while self.noTourFoundAndTimeNotUp(self.areAllCitiesInTour(cities, tour), startTime, timeAllowance):
			closestCity: dict = self.getClosestCity(currCity, cities, tour)
			
			tour.append(closestCity['city'])
			cities.remove(closestCity['city'])
			currCity = closestCity['city']

		endTime = time.time()

		results: dict = {
			'cost': self.getCostOfTour(tour) if self.areAllCitiesInTour(cities, tour) else math.inf,
			'time': endTime - startTime,
			'count': 1,
			'soln': TSPSolution(tour),
			'max': None,
			'total': None,
			'pruned': None
		}

		self.bssf = results
		return results

	def getCostOfTour(self, tour: list[City]):
		tour: list[City] = copy.deepcopy(tour)
		totalDistance: float = 0
		currCity: City = tour.pop(0)

		while len(tour) > 0:
			nextCity = tour.pop(0)
			totalDistance += currCity.costTo(nextCity)
			currCity = nextCity

		return totalDistance


	def getClosestCity(self, currCity: City, cities: list[City], tour: list[City]) -> dict:
		closest: dict = {
			'city': None,
			'distance': float('inf')
		}
				
		for toCity in cities:
			if self.isClosestAndNotAlreadyInTour(currCity, toCity, closest, tour):
				closest = {
					'city': toCity,
					'distance': currCity.costTo(toCity)
				}
			
		return closest
	
	def isClosestAndNotAlreadyInTour(self, currCity: City, toCity: City, closest: dict, tour: list[City]):
		return (currCity.costTo(toCity) < closest['distance']) and (toCity not in tour)

	def areAllCitiesInTour(self, cities: list[City], tour: list[City]):
		return not (len(self._scenario.getCities()) > len(tour))

	def noTourFoundAndTimeNotUp(self, foundTour: bool, startTime: time, timeAllowance: float):
		return not foundTour and time.time()-startTime < timeAllowance


	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints:
		max queue size, total number of states created, and number of pruned states.</returns>
	'''

	def branchAndBound(self, timeAllowance):
		cities: list[City] = copy.deepcopy(self._scenario.getCities())

		startTime: time = time.time()		
		# get init estimate with greedy solution
		self.greedy(timeAllowance)

		costMatrix: dict = self.createCostMatrix(cities)
		lowerBound: float
		reducedMatrix: dict
		lowerBound, reducedMatrix = self.computeLowerBoundAndReduce(costMatrix, [])

		priorityQueueLength: list = []
		heapq.heapify(priorityQueueLength)
		heapq.heappush(priorityQueueLength, (-1, self.getCounter(), {
			'lowerBound': lowerBound,
			'reducedMatrix': reducedMatrix,
			'path': ['A']
		}))

		priorityQueueLB: list = []
		heapq.heapify(priorityQueueLB)
		heapq.heappush(priorityQueueLB, (lowerBound, self.getCounter(), {
			'lowerBound': lowerBound,
			'reducedMatrix': reducedMatrix,
			'path': ['A']
		}))

		lengthPQ = 1
		while len(priorityQueueLB) > 0 and time.time()-startTime < timeAllowance:
			if lengthPQ // 3 != 0:
				_, __, currSubproblem = heapq.heappop(priorityQueueLength)
				lengthPQ += 1

				priorityQueueLB = [item for item in priorityQueueLB if item[2] != currSubproblem]
			else:
				_, __, currSubproblem = heapq.heappop(priorityQueueLB)
				lengthPQ += 1

				priorityQueueLength = [item for item in priorityQueueLength if item[2] != currSubproblem]

			
			if currSubproblem['lowerBound'] < self.bssf['cost']:
				self.expandSubproblem(currSubproblem, self.bssf, priorityQueueLB, priorityQueueLength)
			else:
				self.pruned += 1

		endTime = time.time()


		results: dict = {
			'cost': self.bssf['cost'],
			'time': endTime - startTime,
			'count': self.numOfBSSFUpdates,
			'soln': TSPSolution(self.createSolution(self.bssf['path'], cities)),
			'max': self.maxPriorityQueueLen,
			'total': self.numOfStatesCreated,
			'pruned': self.pruned,
			'bssfUpdates': self.numOfBSSFUpdates
		}

		return results
	
	def createSolution(self, path, cities):
		retList = []

		for city in path:
			for cit in cities:
				if city == cit._name:
					retList.append(cit)

		return retList


	def expandSubproblem(self, subProblem: dict, BSSF: dict, priorityQueueLB: list, priorityQueueLength: list):
		parentLowerBound: float = subProblem['lowerBound']
		matrix: dict = subProblem['reducedMatrix']
		fromCity: str = subProblem['path'][-1]
		
		for toCity in matrix[fromCity]:
			self.numOfStatesCreated += 1
			path: list = copy.deepcopy(subProblem['path'])
			path.append(toCity)
			edgeCost: float = matrix[fromCity][toCity]
			infinitizedMatrix: dict = self.infinitize(matrix, fromCity, toCity)
			costOfReduction, reducedInfinitizedMatrix = self.computeLowerBoundAndReduce(infinitizedMatrix, path)
			lowerBound = parentLowerBound + edgeCost + costOfReduction

			if lowerBound < self.bssf['cost']:
				if len(path) == len(matrix):
					self.bssf = {
						'cost': lowerBound,
						'time': None,
						'count': None,
						'soln': None,
						'max': None,
						'total': None,
						'pruned': None,
						'path': path
					}
					self.numOfBSSFUpdates += 1
				else:
					heapq.heappush(priorityQueueLB, (lowerBound, self.getCounter(), {
						'lowerBound': lowerBound,
						'reducedMatrix': reducedInfinitizedMatrix,
						'path': path
					}))

					heapq.heappush(priorityQueueLength, (-1 * len(path), self.getCounter(), {
						'lowerBound': lowerBound,
						'reducedMatrix': reducedInfinitizedMatrix,
						'path': path
					}))

					if (len(priorityQueueLength) > self.maxPriorityQueueLen) or (len(priorityQueueLB) > self.maxPriorityQueueLen):
						self.maxPriorityQueueLen = max(len(priorityQueueLength), len(priorityQueueLB))
			else:
				self.pruned += 1


	def infinitize(self, matrix: dict, fromCity: str, toCity: str):
		matrix: dict = copy.deepcopy(matrix)

		for colKey in matrix[fromCity]:
			matrix[fromCity][colKey] = float('inf')

		for rowKey in matrix:
			matrix[rowKey][toCity] = float('inf')
		
		matrix[toCity][fromCity] = float('inf')

		return matrix


	def computeLowerBoundAndReduce(self, costMatrix: dict, path: list) -> [float, dict]:
		fromCities: list[str] = path[:-1]
		toCities: list[str] = path[1:]
		costOfReduction: float = 0

		# reduce all rows
		for rowKey in costMatrix:
			if rowKey not in fromCities:
				row: dict = costMatrix[rowKey]
				lowestValueInRow = self.getLowestValueInRow(row, toCities)
				if lowestValueInRow != None:
					costOfReduction += lowestValueInRow
					for colKey in row:
						if costMatrix[rowKey][colKey] != float('inf'):
							costMatrix[rowKey][colKey] -= lowestValueInRow

		# reduce all columns
		for colKey in costMatrix['A']:
			if colKey not in toCities:
				minColumnValue: float = float('inf')
				for rowKey in costMatrix:
					if costMatrix[rowKey][colKey] < minColumnValue:
						minColumnValue = costMatrix[rowKey][colKey]
				
				if minColumnValue != float('inf'):
					costOfReduction += minColumnValue
					for rowKey in costMatrix:
						costMatrix[rowKey][colKey] -= minColumnValue

		return costOfReduction, costMatrix

	def getLowestValueInRow(self, row: dict, toCities: list[str]):
		lowestValue: float = None
		for toCity in row:
			if toCity not in toCities:
				if lowestValue == None or row[toCity] < lowestValue:
					lowestValue = row[toCity]
		
		return lowestValue


	def createCostMatrix(self, cities: list[City]):
		costMatrix: dict = {}
		for fromCity in cities:
			costMatrix[fromCity._name]: dict = {}
			for toCity in cities:
				if fromCity == toCity:
					costMatrix[fromCity._name][toCity._name] = float('inf')
				else:
					costMatrix[fromCity._name][toCity._name] = fromCity.costTo(toCity)
		
		return costMatrix
