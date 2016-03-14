# Feature Refresher
## A tool to use with our SLAM system
------------------------------------------

Before doing anything, make sure to generate asmany KML files as you need for your output. I would think about 100000 is a good estimate, but ultimately it depends on your SLAM system.

Then, push your output into the main thread, as such:

`python print_real_time <filename> | python plot_refresh_threaded.py`

If you have a real-time system, just pipe it into the script.