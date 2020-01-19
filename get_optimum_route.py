
import collections
import numpy as np

def get_optimum_route(CURRENT,SOURCE,DESTINATION,TRAVELTIME,servicetime = [],MaxHours = [],dist_mat = [],G = [],path = [],distance = 0,totaltime = 0,maxJobsCompleted = 0):
	
	"""
	CURRENT 	-- dtype | tuple (latitude,longitude)
	SOURCE 				-- dtype | list of tuples [(latitude,longitude),...(latitude,longitude)]
	DESTINATION 		-- dtype | list of tuples [(latitude,longitude),...(latitude,longitude)]
	TRAVELTIME			-- dtype | dict {(source[i],destination[j]) : travel time in Hours from source[i] to destination[j]}
	servicetime			-- dtype | dict {(source[i]) or (destination[j]) : service time in Hours} (optional)
	MaxHours			-- dtype | int Max hours of work (optional, default : 10)
	dist_mat 			-- dtype | dict {(source[i],destination[j]) : distance between source[i] to destination[j]} (optional, default : Manhatten distance)
	G 					-- dtype | dict {(source[i]) or (destination[j]) : list of connected sources and destinations} (optional)
	
	Arguments (path,distance,totaltime,maxJobsCompleted) are used for recursion purpose
	Input : 
		CURRENT : include GPS co-ordinations (latitude,longitude)
		SOURCE : include GPS co-ordinates of source locations of open tasks
		DESTINATION : include GPS co-ordinates of destination locations of open tasks
			*Note: length of source and destination should be equal
		TRAVELTIME : Time required to travel between all pairs of sources and destinations
			key elements in traveltime are of the form (source[i],destination[i]) or (source[i],source[j]) ...
		servicetime : Time required at each source and destination for loading/unloading (optional)
		Maxhours : Maximum work hours left (optional)
		dist_mat : Distance matrix from all pairs of source and destination locations (optional)
		G : Graph denoting valid connections for all sources and destinations (optional)

	Output : 
		dtype | tuple (shortest_path, shortest_distance, shortest_time, maxJobsCompleted)
		optimal_path : shortest path estimated by algorithm
		optimal_distance : distance travelled by the shortest path
		optimal_time : total estimated time by the shortest path
		maxJobsCompleted : maximum number of jobs completed by the shortest path

	Example :
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
	"""
	#------------------------------------------ Check input parameters-------------------------------------------
	if not MaxHours:
		MaxHours = 10
	# Form a graph denoting valid connections between source and destination locations
	if not G: 
		G = collections.defaultdict(list)
		if CURRENT not in SOURCE and CURRENT not in DESTINATION: # The starting point is not in the list of source and destinations
			for i in range(len(SOURCE)):
				G[CURRENT].append(SOURCE[i])
		for i in range(len(SOURCE)): # Connect each source to its destination
			G[SOURCE[i]].append(DESTINATION[i])
			
			for j in range(len(SOURCE)): # Connect each source to other sources
				if i != j:
					G[SOURCE[i]].append(SOURCE[j])

		for i in range(len(DESTINATION)): # Connect each destination to other sources
			for j in range(len(SOURCE)):
				if i != j:
					G[DESTINATION[i]].append(SOURCE[j])
			for j in range(len(DESTINATION)): # Connect each destination to other destinations
				if i != j:
					G[DESTINATION[i]].append(DESTINATION[j])
	#---------------------------------------------------------------------------------
	# Part 1 : Update path and metrics based on current location
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
	#---------------------------------------------------------------------------------
	# Part 2 : Check if the updated path satisfies the conditions
	# Check if the current path follows the order and calculate the number of jobs completed by the path
	numjob = 0
	for i in range(len(SOURCE)):
		if SOURCE[i] in path and DESTINATION[i] in path and path.index(SOURCE[i]) < path.index(DESTINATION[i]): #ith job is complete
			numjob += 1
	
	# If all jobs are completed in the time limit return
	if numjob == len(SOURCE) and totaltime < MaxHours:
		return path, distance, totaltime, numjob
	# If number of jobs completed greater than max jobs completed by previous searced paths return
	if numjob > maxJobsCompleted and totaltime < MaxHours:
		return path, distance, totaltime, (numjob)

	#---------------------------------------------------------------------------------
	# Part 3 : Search for next valid location from current location
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

	return optimal_path, optimal_distance, optimal_time, maxJobsCompleted
