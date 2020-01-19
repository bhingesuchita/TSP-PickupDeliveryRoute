import pandas as pd
import numpy as np
import datetime
from get_optimum_route import *
import herepy

routingApi = herepy.RoutingApi('YOUR_API_KEY')

"""
#-------------------------------- Modify columns --------------------------
data = pd.read_csv('updated_data_task.csv')
new_data = pd.DataFrame(columns=[])
new_data['Serial Number'] = data['Serial Number']

# Modify start_time and end_time to separate the date and time
for i in range(len(data.start_time)):
	if not pd.isnull(data.loc[i,'start_time']):
		date = datetime.datetime.strptime(data.loc[i,'start_time'], "%m/%d/%y  %H:%M")
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'start_date'] = date.date()
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'start_time'] = date.time()
	if not pd.isnull(data.loc[i,'end_time']):
		date = datetime.datetime.strptime(data.loc[i,'end_time'], "%m/%d/%y  %H:%M")
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'end_date'] = date.date()
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'end_time'] = date.time()

# Convert source service time to hours
for i in range(len(data.source_service_time)):
	if not pd.isnull(data.loc[i,'source_service_time']):
		temp = data.loc[i,'source_service_time'].split()
		
		time = datetime.datetime.strptime(temp[2].split('.')[0], "%H:%M:%S")
		time_tohours = time.hour + time.minute/60 + time.second/3600
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'source_service_time'] = time_tohours

# Convert destination service time to hours
for i in range(len(data.dest_service_time)):
	if not pd.isnull(data.loc[i,'dest_service_time']):
		temp = data.loc[i,'dest_service_time'].split()
		time = datetime.datetime.strptime(temp[2].split('.')[0], "%H:%M:%S")
		time_tohours = time.hour + time.minute/60 + time.second/3600
		new_data.loc[new_data['Serial Number']==data['Serial Number'].iloc[i],'dest_service_time'] = time_tohours

# Remove unwanted columns from previous data frame
data.pop('start_time')
data.pop('end_time')
data.pop('source_service_time')
data.pop('dest_service_time')

# Merge modified dataframe with previous data frame
data = pd.merge(data,new_data,on='Serial Number')

# Save new data frame
data.to_csv(r'New_data_Jan14.csv', index=False)
# ---------------------------------------------------------------------------------------------------
"""
# Read new data frame for analysis
data = pd.read_csv('New_data_Jan14.csv')

# Get source destination associated with each job, store in 'jobID'
temp = data.groupby(['job_id','source_lat','source_lon','dest_lat','dest_lon']).groups.keys()
jobID = {}
for keys in temp:
	jobID[keys[0]] = [(keys[1],keys[2]),(keys[3],keys[4])]

# Get aerage source and destination service time for each job
meanSourceServiceTime = data.groupby(['job_id','source_lat','source_lon','dest_lat','dest_lon'])['source_service_time'].mean()
meanDestServiceTime =  data.groupby(['job_id','source_lat','source_lon','dest_lat','dest_lon'])['dest_service_time'].mean()

# Define max work hours
maxWorkHours = 10

# Run on few examples
example = [(0,'2019-07-11'),(63,'2019-08-28'),(155, '2019-11-13')]
# Loop through the job list for each driver on every day to get the optimum route
for key in example:
	if not pd.isnull(key[0]) and not pd.isnull(key[1]):
		# Create a list of jobs for each day
		job_list = data[(data['driver_id'] == key[0]) & (data['start_date'] == key[1])]['job_id']

		# Get the corresponding source, destination information for the jobs
		source = []
		destination = []
		servicetime = {}
		for j in job_list:
			source.append(jobID[j][0])
			servicetime[jobID[j][0]] = meanSourceServiceTime[j][0]
			destination.append(jobID[j][1])
			servicetime[jobID[j][1]] = meanDestServiceTime[j][0]

		# Get the estimated travel time and distance between each pair of locations using HERE maps API
		traveltime = {}
		nodes = list(set(source + destination))
		DIST_MAT = {}
		for i in nodes:
			for j in nodes:
				if i != j:
					response = routingApi.truck_route(i,j,[herepy.RouteMode.fastest, herepy.RouteMode.truck])
					traveltime[(i,j)] = response.response.get('route')[-1].get('summary').get('baseTime')/3600 # convert seconds to hours
					DIST_MAT[(i,j)] = response.response.get('route')[-1].get('summary').get('distance')/1609.34 # convert meters to miles

		# Get the optimum route for each driver on each day
		out = get_optimum_route(source[0],source,destination,traveltime,servicetime,maxWorkHours,DIST_MAT)

		# Print results
		print('Driver ID:', key[0], 'Date:', key[1], '--')
		print('Source locations: ', source)
		print('Destination locations: ', destination)
		print('------------------------')
		print('Route: ', out[0])
		print('Estimated distance: ', out[1], 'miles')
		print('Estimated time (travel + service time): ', out[2], 'hours')
		print('Est. number of completed jobs: ', out[3])
		print('\n')

print('Try other examples from list:')
# To get the job IDs for each driver on each day, group the data by driver_id and start_date 
df = data.groupby(['driver_id','start_date'])

# Get unique combinations of driver ID and start date  
driverIDs = df.groups.keys()
print(driverIDs)