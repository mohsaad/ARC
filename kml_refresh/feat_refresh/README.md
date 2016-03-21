# Feature Refresher
## A tool to use with our SLAM system
------------------------------------------

Before doing anything, make sure to generate as many KML files as you need for your output using 

`python generate_refresh_files.py <filename> <number of files>` 

I would think about 100000 is a good estimate, but ultimately it depends on your SLAM system.

Then, push your output into the main thread, as such:

`python print_real_time <filename> | python plot_refresh_threaded.py`

If you have a real-time system, just pipe it into the script. Each trajectory point should have the format (all coordinates in UTM):

`Time,Easting,Northing,z,...`

The feature points should have the format (again in UTM):

`FeatureID, Easting, Northing, z, ...`

Having the output in this format ensures that this code will be able to decode and plot it correctly.


