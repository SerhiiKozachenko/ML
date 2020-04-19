from UACovid import UACovid

# Init unit of work
n = UACovid()

# Load latest data
n.load()


# Process data
n.process()

# Print top 5 rows
#n.print_top_5_rows()

#n.print_totals()

#n.print_date_stats()

#n.print_area_stats(area='Харківська',last_30_days=True)

# Draw charts
n.draw_charts_for_area(area='Харківська',last_30_days=True)

# Draw charts for multiple states - comparison for last 30 days
# n.plot_multi_state(states=['California', 'Michigan', 'Georgia','Illinois'],
#                   last_30_days=True)


#n.rankState(N=6)

#n.rankState(N=4,daterank='2020-03-26')
