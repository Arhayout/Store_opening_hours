#imports
import pandas as pd
import numpy as np
import datetime


# Step 1: Preprocess the data

# Load the dataset into a dataframe
df = pd.read_csv('data.csv')
# Compute the number of NaN values in each column
nan_counts = df.isna().sum()

# Compute the number of NaT values in a specific column
nat_count = df['device_local_date'].isnull().sum()

# Print the results
print("NaN counts:")
print(nan_counts)
print("\nNaT count in 'device_local_date' column:")
print(nat_count)

#  Convert 'device_local_date' to datetime format
df['device_local_date'] = pd.to_datetime(df['device_local_date'], format='%Y-%m-%d %H:%M:%S')

#  Extract the time from 'device_local_date' column
df['device_local_time'] = df['device_local_date'].dt.time

#  Extract day of the week
df['day_of_week'] = df['device_local_date'].dt.dayofweek
grouped_df = df.groupby(['shopping_center_id', 'day_of_week'])

grouped_df.head()
grouped_df['device_local_date'].head()




# Step 2: Calculate earliest and latest visit times
opening_hours = {}
for group, data_grouped_df in grouped_df:
    shopping_center_id, day_of_week = group
    min_time = data_grouped_df['device_local_time'].min()
    max_time = data_grouped_df['device_local_time'].max()

    # Calculate opening hours
    opening_hours.setdefault(shopping_center_id, {}).setdefault(day_of_week, (min_time, max_time))

#Print opening hours for each shopping center and day of the week
for shopping_center, opening_hours_per_center in opening_hours.items():
    print(f"Shopping Center: {shopping_center}")
    for day_of_week, hours in opening_hours_per_center.items():
        start_time, end_time = hours
        print(f"Day of the week: {day_of_week}")
        print(f"Opening hours: {start_time} - {end_time}\n")

# Step 3: Calculate the average opening hours for each day of the week
average_hours = {}
average_min ={}
for day in range(7):
    hours = []
    min = []
    for center_id, center_hours_per_day in opening_hours.items():
        if day in center_hours_per_day:
            min_time, max_time = center_hours_per_day[day]
            opening_duration = datetime.datetime.combine(datetime.datetime.min.date(), max_time) - datetime.datetime.combine(datetime.datetime.min.date(), min_time)
            hours.append(opening_duration.total_seconds())
            #opening = datetime.datetime.combine(datetime.datetime.min.date(), min_time)
            #min.append(opening.total_seconds())
    if len(hours) > 0:
        average_hours[day] = pd.Timedelta(seconds=np.mean(hours))
        #average_min[day] = pd.Timedelta(seconds=np.mean(min))

    else:
        average_hours[day] = pd.NaT

# Step 4 :Using this average to predict new center openings

new_center_id = "b43e9e4f-acd1-4941-874d-e0c5650ab91e"
new_center_data = df[df['shopping_center_id'] == new_center_id]

new_center_hours = {}
parsed_average_hours = [datetime.datetime.strptime(str(datetime.timedelta(seconds=average_hours[h].seconds)), "%H:%M:%S").time() for h in average_hours]

def time_difference(z, t):
    datetime_average = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    min_diff = datetime.timedelta.max  # Initialize with maximum timedelta
    min_indices = ()
    for i in range(len(z)):
        datetime1 = datetime.datetime.combine(datetime.datetime.min.date(), z[i])
        for j in range(len(z)):
            if z[i] > z[j]:
                
                datetime2 = datetime.datetime.combine(datetime.datetime.min.date(), z[j])
                time_diff = abs(datetime1 - datetime2 - datetime_average)
                if time_diff < min_diff:
                    min_diff = time_diff
                    min_indices = (i, j)
    return min_indices, min_diff


for day in range(7):
    if day in new_center_data['day_of_week'].values:
        center_hours_per_day = new_center_data[new_center_data['day_of_week'] == day]['device_local_time'].reset_index(drop=True)
        closest_hour_index, _ = time_difference(center_hours_per_day, parsed_average_hours[day])
        closest_hour = (center_hours_per_day[closest_hour_index[1]], center_hours_per_day[closest_hour_index[0]])
        new_center_hours[day] = closest_hour
    else:
        new_center_hours[day] = pd.NaT


# Print the opening hours for the new center
print(f"Opening Hours for New Center ({new_center_id}):")
for day_of_week, hours in new_center_hours.items():
    end_time, start_time = hours
    print(f"Day of the week: {day_of_week}")
    print(f"Opening hours: {start_time} - {end_time}\n")


        


