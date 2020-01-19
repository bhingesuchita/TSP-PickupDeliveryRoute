# TSP-PickupDeliveryRoute

Description – The goal of travelling salesman problem is to find the shortest path connecting all cities from a given list of cities and distances between each pair of cities. A typical pickup-delivery type scenario requires the solution to satisfy some conditions while solving the travelling salesman problem. Some of the conditions are given below.
1. The path taken to visit the cities must follow a certain order, i.e., the path must visit a pickup location prior to a delivery location. 
2. The total time must be within a certain working hour limit, where the total time includes the travel time between different locations, time spent at the pickup and delivery location and break time.
3. The objective is to maximize the number of deliveries within a certain working hour limit and minimize the distance travelled by the vehicle.

Problem formulation –
A graph-based approach is used to solve the TSP while considering the conditions mentioned above. As a first step, we generate a directional graph denoting all the valid directions a search path can take. The valid connections are given as follows:
a. The vehicle can travel from one source to its own destination, but not otherwise.
b. The vehicle can travel from one source to other sources, but not other destinations.
c. The vehicle can travel from one destination to other sources and other destinations.
The first two conditions avoid the vehicle to travel to the destination prior to the corresponding source, whereas the third condition allows the vehicle to travel to multiple source locations prior to travelling to the corresponding delivery locations. 

Implementation –
First, import all necessary libraries. We will use `defaultdict` from `collections` to generate the graph.
```
import collections
```
We use a recursive approach to search for an optimal path that satisfies the conditions mentioned in description section. The function can be divided into three parts:
1. Update parameters of the path based on current location
2. Check if the updated path satisfies the conditions, if yes save this path and its metrics (such as distance, total time and number of jobs it completed)
3. Search for next valid location from current location

Part 1: Update path and the parameters of the path based on current location 
Calculate the distance travelled by the path after adding the current location.
Calculate the total time as the sum of travel time from previous location to current location and service time at current location. The service time accounts for time required to load and unload the package. It can be ignored if the time is negligible compared to the travel time or is unknown.
```
if path: # If path exists
	if not dist_mat:
		# Calculate distance from previous location to current location using Manhatten distance
		distance += abs(path[-1][0] - CURRENT[0]) + abs(path[-1][1] - CURRENT[1])
	else:
		distance += dist_mat[(path[-1],CURRENT)]

	# Calculate total travel time required from previous location to current location plus service time at current location
	if servicetime:
		totaltime += TRAVELTIME[(path[-1],CURRENT)] + servicetime[CURRENT] 
	else: # Service time is either negligible compared to traveltime or unknown
		totaltime += TRAVELTIME[(path[-1],CURRENT)] 


# Add current location to path
path = path + [CURRENT]
```

Part 2: Check if the updated path satisfies the conditions 
This section checks if the path is valid, i.e., for each package delivery task, if the source location is visited prior to the destination location.
Additionally, it calculated the number of jobs completed by the updated path. We return the updated path if 
A. all tasks are completed within the working hour limit or B. if the number of tasks completed are greater than the maximum number of jobs completed by the previous search paths.  
We save the returned path as the optimal path if the distance travelled is less than the shortest distance travelled or if the number of jobs completed is greater than the maximum number of jobs completed by the previous search paths.
```
numjob = 0
for i in range(len(SOURCE)):
	if SOURCE[i] in path and DESTINATION[i] in path and path.index(SOURCE[i]) < path.index(DESTINATION[i]): 
		numjob += 1

# If all jobs are completed in the time limit return
if numjob == len(SOURCE) and totaltime < MaxHours:
	return path, distance, totaltime, numjob
# If number of jobs completed greater than max jobs completed by previous searced paths return
if numjob > maxJobsCompleted and totaltime < MaxHours:
	return path, distance, totaltime, (numjob)
```

Part 3: Search for next valid location
This section searches for the next location from the list of next valid locations for the current location denoted in the graph. A location that is not located in the path is selected and parts 1 to 3 are repeated.
```
optimal_path = None
optimal_distance = 10000
optimal_time = None

for NODE in G[CURRENT]:
	if NODE not in path:
		newpath, newdistance, newtime, JobsCompleted = get_optimum_route(NODE,SOURCE,DESTINATION,TRAVELTIME,servicetime,
			MaxHours,dist_mat,G,path,distance,totaltime,maxJobsCompleted)

		if not optimal_path or (JobsCompleted == maxJobsCompleted and newdistance < optimal_distance) or (JobsCompleted > maxJobsCompleted):
			optimal_path = newpath
			optimal_distance = newdistance
			optimal_time = newtime
			maxJobsCompleted = JobsCompleted
```


Future scope:
The proposed algorithm assumes that the capacity of the vehicle is equal to greater than the total capacity of packages. If there are limitations on the capacity of the vehicle, the conditions in part 2 of the algorithm can be updated to incorporate capacity constraints. In some cases, the priority of certain deliveries is higher than others, in which case a weighted graph can be used. For the weighted graphs the weight of priority locations can be set higher than others and these locations can be picked based on their weights in part 3 of the algorithm.

Example:
```
source = [(0,0),(0,0),(3,1)] 
destination = [(2,2),(2,2),(1,1)]
starting_point = [(-1,-1)]

nodes = list(set(source + destination + starting_point))

traveltime = {}
for i in nodes:
	for j in nodes:	
		if i != j:
			traveltime[(i,j)] = np.random.uniform()
		
out = get_optimum_route(starting_point[-1],source,destination,traveltime)

print('Route: ', out[0])
print('Estimated distance: ', out[1])
print('Estimated time: ', out[2])
print('Est. number of completed jobs: ', out[3])

```
