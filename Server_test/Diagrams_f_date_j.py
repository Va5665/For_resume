import sqlite3
import sys
from datetime import datetime
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure, show, output_file
from bokeh.models import LabelSet
if len(sys.argv) != 3:
    print("Usage: python Diagrams_f_date_j.py <start_date> <end_date>")
    sys.exit(1)
start_date = sys.argv[1]
end_date = sys.argv[2]
conn = sqlite3.connect('../../pythonProject/cag10/mydatabase_Films.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM statistics_films WHERE date BETWEEN ? AND ?', (start_date, end_date))
results = cursor.fetchall()
for row in results:
    print(row)
dates = [datetime.strptime(row[1], '%Y-%m-%d') for row in results]
last_ok = [row[2] for row in results]
last_bad = [row[3] for row in results]
dates_sorted = sorted(dates)
p = figure(x_axis_type='datetime', title='Content Statistics', height=int(0.8 * 800), width=800, sizing_mode='stretch_both')


output_file('results/All_Films_diagramm.html')
p.line(dates, last_ok, legend_label='OK Films', line_color='green', line_width=5)
p.line(dates, last_bad, legend_label='Bad Films', line_color='red', line_width=10)
source_ok = ColumnDataSource(data=dict(date=dates, value=last_ok))
source_bad = ColumnDataSource(data=dict(date=dates, value=last_bad))
labels_ok = LabelSet(x='date', y='value', text='value', level='glyph',
                     x_offset=5, y_offset=15, source=source_ok, text_color='green',
                     text_baseline='middle')
labels_bad = LabelSet(x='date', y='value', text='value', level='glyph',
                      x_offset=5, y_offset=-15, source=source_bad, text_color='red',
                      text_baseline='middle')
p.add_layout(labels_ok)
p.add_layout(labels_bad)
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Content Count'
show(p)
conn.close()
