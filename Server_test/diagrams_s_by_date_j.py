import sqlite3
import sys
from datetime import datetime
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.models import LabelSet

if len(sys.argv) != 3:
    print("Usage: python diagrams_s_by_date_j.py <start_date> <end_date>")
    sys.exit(1)
start_date = sys.argv[1]
end_date = sys.argv[2]
conn = sqlite3.connect('../../pythonProject/cag10/mydatabase.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM statistics WHERE date BETWEEN ? AND ?', (start_date, end_date))
results = cursor.fetchall()
for row in results:
    print(row)
dates = [datetime.strptime(row[1], '%Y-%m-%d') for row in results]
total_tested_serials = [row[2] for row in results]
last_ok_serials = [row[3] for row in results]
last_bad_serials = [row[4] for row in results]

dates_sorted = sorted(dates)

p = figure(x_axis_type='datetime', title='Content Statistics', height=int(0.8 * 800), width=800, sizing_mode='stretch_both')
output_file('tests_Serials/All_diagramm.html')
p.line(dates, last_ok_serials, legend_label='OK Serials', line_color='green', line_width=10)
p.line(dates, last_bad_serials, legend_label='Bad Serials', line_color='red', line_width=15)
p.line(dates, total_tested_serials, legend_label='total_tested_serials', line_color='blue', line_width=5)

source_ok_serials = ColumnDataSource(data=dict(date=dates_sorted, value=last_ok_serials))
source_bad_serials = ColumnDataSource(data=dict(date=dates_sorted, value=last_bad_serials))
total_tested_serials = ColumnDataSource(data=dict(date=dates_sorted, value=total_tested_serials))

labels_ok_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                             x_offset=5, y_offset=15, source=source_ok_serials, text_color='green', text_baseline='middle')
labels_bad_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                              x_offset=5, y_offset=-15, source=source_bad_serials, text_color='red', text_baseline='middle')
total_tested_serials = LabelSet(x='date', y='value', text='value', level='glyph',
                              x_offset=5, y_offset=30, source=total_tested_serials, text_color='blue', text_baseline='middle')

p.add_layout(labels_ok_serials)
p.add_layout(labels_bad_serials)
p.add_layout(total_tested_serials)

p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Content Count'
show(p)
conn.close()

