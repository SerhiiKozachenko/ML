from NYTCovid import NYTCovid

# Init unit of work
n = NYTCovid()

# Load latest data
n.updateState()

# Check that data was loaded and print the last date
n.dateUpdate()

# Print top 5 rows
n.peek()

# Process data - generate dict with state as a keys using panda data frame
# add in new cases and new deaths columns
n.process()

# Draw charts for Californina last 30 days
#n.plot_state(state='California',last_30_days=True)

# Draw charts for multiple states - comparison for last 30 days
n.plot_multi_state(states=['California', 'Michigan', 'Georgia','Illinois'],
                  last_30_days=True)


#n.rankState(N=6)

#n.rankState(N=4,daterank='2020-03-26')
