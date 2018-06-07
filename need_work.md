
## Things to be worked on:
1. <s>Figure out a way to make 25km optional</s>
  1. <s>Maybe add a boolean for high or low resolution analysis?</s>
2. maybe add back in concatenation at each 100 days
  1. or switch it to do a year at a time, and then the year can be a part of the file name for each sub-concatenation
3. what should I do when a user wants to scrape and concatenate but not subset?
  1. bounding box = none
  2. Current Problem:
    1. the subset function adds the file path for the subsetted files when working, so the downloaded files still have no file path, they are just in the wget folder
    2. FIX: change cwd to wget in concatenate when the user isnt subsetting 



NewList:
1. <s>remove my default username and password, in favor of looking for the .netrc file</s>

2. <s>test swepy with M grid (between -40 and 40)</s>
  1. need to decide on new cutoff, should look at some images and decide where the N and S grids lose the majority of their data and make that the cutoff point
    1. or, I could do some weird way of getting both and stiching them together (avg overlap maybe?) But they are in different projections and that would be shitty
    2. Maybe instead, if a user enters a study area that could be either, I let them choose??
      1. could calculate the percentage of data available in the study area and then give an option for either (but that would require scraping and opening a file to figure it out)

3. Figure out what to do with the 'edge cases'

3. Fix plot_a_day
    - it is integrated into the class, but not showing any data
    - want to speed up the building of the dataframe
    - first fix missing visible data on maps




Testing Order:
1. make new conda env with yml file
2. install swepy via pip
3. install ipykernel spec and open jupyter tqdm_notebook
4. attempt to instantiate the class
5. call the scape_all function

Things to check functionality:
2. any way to use conda-forge for dependencies?
3. package not installable with conda yet
