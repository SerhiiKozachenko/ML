#!/usr/bin/python
# -*- coding: utf-8 -*-

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

n.print_area_stats(area='Харківська',last_30_days=True)

# Draw charts
n.draw_charts_for_area(area='Харківська',last_30_days=True)

# Draw charts for multiple areas
n.draw_charts_for_multi_areas(areas=['Харківська','Дніпропетровська','м. Київ', 'Київська', 'Чернівецька'],
                              last_30_days=True)


n.rank_area(N=6)

#n.rankState(N=4,daterank='2020-03-26')
