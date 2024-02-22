#!/usr/bin/python3


from CS312Graph import *
import time
import copy

class NetworkRoutingSolver:
    def __init__(self):
        pass

    def initializeNetwork( self, network: CS312Graph ):
        assert( type(network) == CS312Graph )
        self.network = network

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        total_length = 0
        node = self.network.nodes[self.dest]

        nextNode = node.previousNode
        for edge in nextNode.neighbors:
            if edge.dest.node_id == node.node_id:
                path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
                total_length += edge.length
                break
        node = nextNode

        while nextNode.previousNode != None:
            nextNode = node.previousNode
            for edge in nextNode.neighbors:
                if edge.dest.node_id == node.node_id:
                    path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
                    total_length += edge.length
                    node = nextNode
                    break

        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths(self, srcIndex: int, use_heap:bool = False):
        self.source = srcIndex

        t1 = time.time()

        for node in range(len(self.network.nodes)):
            self.network.nodes[node].distanceToStartNode = float('inf')
            self.network.nodes[node].removed = False
            self.network.nodes[node].previousNode = None
        
        self.network.nodes[srcIndex].distanceToStartNode = 0

        if use_heap:
            # heap implementation
            priorityQueue: HeapPQ = HeapPQ()
            priorityQueue.makeQueue(self.network.nodes)
            deletes = 0

            while priorityQueue.isNotEmpty():
                closestNode: CS312GraphNode = priorityQueue.deleteMin(self.network.nodes)
                for edge in closestNode.neighbors:
                    if self.network.nodes[edge.dest.node_id].distanceToStartNode > closestNode.distanceToStartNode + edge.length:
                        self.network.nodes[edge.dest.node_id].distanceToStartNode = closestNode.distanceToStartNode + edge.length
                        edge.dest.distanceToStartNode = closestNode.distanceToStartNode + edge.length
                        self.network.nodes[edge.dest.node_id].previousNode = closestNode
                        edge.dest.previousNode = closestNode
                        priorityQueue.decreaseKey(edge.dest)

        else:
            # array implementation
            priorityQueue: ArrayPQ = ArrayPQ()
            priorityQueue.makeQueue(self.network.nodes)

            while priorityQueue.isNotEmpty():
                closestNode: CS312GraphNode = priorityQueue.deleteMin(self.network.nodes)
                for edge in closestNode.neighbors:
                    if edge.dest.distanceToStartNode > closestNode.distanceToStartNode + edge.length:
                        edge.dest.distanceToStartNode = closestNode.distanceToStartNode + edge.length
                        edge.dest.previousNode = closestNode
                        priorityQueue.decreaseKey(edge.dest)


        t2 = time.time()
        return (t2-t1)
    
class HeapPQ:
    def __init__(self) -> None:
        self.pointerArray: list[int] = []
        self.heapArray: list[CS312GraphNode] = [None]

    def makeQueue(self, network: list[CS312GraphNode]):
        for node in range(len(network)):
            self.insert(network[node])

    def decreaseKey(self, node: CS312GraphNode):
        heapIndex = self.pointerArray[node.node_id]
        self.heapArray[heapIndex].distanceToStartNode = node.distanceToStartNode
        self.heapArray[heapIndex].previousNode = node.previousNode

        while (self.heapArray[heapIndex//2] != None) and self.heapArray[heapIndex] < self.heapArray[heapIndex//2]:
            childNode = self.heapArray[heapIndex]
            parentNode = self.heapArray[heapIndex//2]

            self.heapArray[heapIndex] = parentNode
            self.heapArray[heapIndex//2] = childNode

            self.pointerArray[parentNode.node_id] = heapIndex
            self.pointerArray[childNode.node_id] = heapIndex//2

            heapIndex = heapIndex//2

        while ((len(self.heapArray)-1 >= heapIndex*2) and (self.heapArray[heapIndex] > self.heapArray[heapIndex*2]) or ((len(self.heapArray)-1 >= (heapIndex*2)+1) and (self.heapArray[heapIndex] > self.heapArray[(heapIndex*2)+1]))):
            if self.heapArray[heapIndex*2] < self.heapArray[(heapIndex*2)+1]:
                topNode = self.heapArray[heapIndex]
                bottomNode = self.heapArray[heapIndex*2]

                self.heapArray[heapIndex] = bottomNode
                self.heapArray[heapIndex*2] = topNode

                self.pointerArray[bottomNode.node_id] = heapIndex
                self.pointerArray[topNode] = heapIndex*2

                heapIndex = heapIndex*2
            else:
                topNode = self.heapArray[heapIndex]
                bottomNode = self.heapArray[(heapIndex*2)+1]

                self.heapArray[heapIndex] = bottomNode
                self.heapArray[(heapIndex*2)+1] = topNode

                self.pointerArray[bottomNode.node_id] = heapIndex
                self.pointerArray[topNode] = (heapIndex*2)+1

                heapIndex = (heapIndex*2)+1
            

    def deleteMin(self, network: list[CS312GraphNode]) -> CS312GraphNode:
        returnVal: CS312GraphNode = self.heapArray[1]

        network[returnVal.node_id] = returnVal

        index = 1
        self.heapArray[index].removed = True

        while (len(self.heapArray)-1 >= index*2) and ((self.heapArray[index] > self.heapArray[index*2]) or (self.heapArray[index] > self.heapArray[(index*2)+1])):
            if (len(self.heapArray)-1 == index*2):  
                if self.heapArray[index*2] < self.heapArray[index]:
                    topNode = self.heapArray[index]
                    bottomNode = self.heapArray[index*2]

                    self.heapArray[index] = bottomNode
                    self.heapArray[index*2] = topNode

                    self.pointerArray[bottomNode.node_id] = index
                    self.pointerArray[topNode.node_id] = index*2

                    index = index*2
                else:
                    index += 1
            
            elif self.heapArray[index*2] < self.heapArray[(index*2)+1]:
                topNode = self.heapArray[index]
                bottomNode = self.heapArray[index*2]

                self.heapArray[index] = bottomNode
                self.heapArray[index*2] = topNode

                self.pointerArray[bottomNode.node_id] = index
                self.pointerArray[topNode.node_id] = index*2

                index = index*2

            else:
                topNode = self.heapArray[index]
                bottomNode = self.heapArray[(index*2)+1]

                self.heapArray[index] = bottomNode
                self.heapArray[(index*2)+1] = topNode

                self.pointerArray[bottomNode.node_id] = index
                self.pointerArray[topNode.node_id] = (index*2)+1

                index = (index*2)+1
            
        return returnVal

    def insert(self, node: CS312GraphNode):
        self.heapArray.insert(len(self.heapArray)+1, node)
        self.pointerArray.insert(node.node_id, len(self.heapArray)-1)

        lowerIndex = len(self.heapArray)-1
        higherIndex = (len(self.heapArray)-1)//2
        lowerNode = self.heapArray[lowerIndex]
        higherNode = self.heapArray[higherIndex]

        while higherNode != None and  lowerNode < higherNode:
            self.heapArray[lowerIndex] = higherNode
            self.heapArray[higherIndex] = lowerNode

            self.pointerArray[higherNode.node_id] = lowerIndex
            self.pointerArray[lowerNode.node_id] = higherIndex

            lowerIndex = higherIndex
            higherIndex = higherIndex//2

            lowerNode = self.heapArray[lowerIndex]
            higherNode = self.heapArray[higherIndex]

    def isNotEmpty(self):
        return self.heapArray[1].removed != True

class ArrayPQ:
    def __init__(self) -> None:
        self.queue: list[CS312GraphNode] = []
        self.numberOfNodes = 0

    def makeQueue(self, network: list[CS312GraphNode]):
        for node in network:
            self.insert(node)

    def decreaseKey(self, node: CS312GraphNode):
        self.queue[node.node_id] = node.distanceToStartNode

    def deleteMin(self, network: list[CS312GraphNode]) -> CS312GraphNode:
        minNodeIndex: tuple[int, float] = (None, float('inf'))

        for index in range(len(self.queue)):
            if self.queue[index] < minNodeIndex[1]:
                minNodeIndex = (index, self.queue[index])

        self.queue[minNodeIndex[0]] = float('inf')
        self.numberOfNodes -= 1

        return network[minNodeIndex[0]]
    

    def insert(self, node: CS312GraphNode):
        self.queue.append(node.distanceToStartNode) 
        self.numberOfNodes += 1

    def isNotEmpty(self):
        return not all_inf(self.queue)

def all_inf(arr):
    for item in arr:
        if item != float('inf'):
            return False
    return True