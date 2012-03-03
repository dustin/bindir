#!/usr/bin/env python
"""A collection of git info aggregators for graph commands."""

import time
import subprocess
from collections import defaultdict

class TimeHisto(object):

    def __init__(self):
        self.h = defaultdict(lambda: 0)

    def add_logs(self, directory=None, log_args=['HEAD']):
        args=['git']
        if directory:
            args.append('--git-dir=' + directory)
        args.extend(['log', '--pretty=format:%at'])
        args.extend(log_args)
        sub = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)

        for l in sub.stdout:
            self.h[time.strftime("%w %H", time.localtime(float(l.strip())))] += 1

    def dump(self):
        for h in range(24):
            for d in range(7):
                sys.stderr.write("%02d %d - %s\n"
                                 % (h, d, self.h["%d %02d" % (d, h)]))

    def to_gchart(self):
        from pygooglechart import ScatterChart
        chart = ScatterChart(800, 300, x_range=(-1, 24), y_range=(-1, 7))

        chart.add_data([(h % 24) for h in range(24 * 8)])

        d=[]
        for i in range(8):
            d.extend([i] * 24)
        chart.add_data(d)

        day_names = "Sun Mon Tue Wed Thu Fri Sat".split(" ")
        days = (0, 6, 5, 4, 3, 2, 1)

        sizes=[]
        for d in days:
            sizes.extend([self.h["%d %02d" % (d, h)] for h in range(24)])
        sizes.extend([0] * 24)
        chart.add_data(sizes)

        chart.set_axis_labels('x', [''] + [str(h) for h  in range(24)] + [''])
        chart.set_axis_labels('y', [''] + [day_names[n] for n in days] + [''])

        chart.add_marker(1, 1.0, 'o', '333333', 25)
        return chart.get_url() + '&chds=-1,24,-1,7,0,20'

        for l in sub.stdout:
            self.h[time.strftime("%w %H", time.localtime(float(l.strip())))] += 1

    def dump(self):
        for h in range(24):
            for d in range(7):
                sys.stderr.write("%02d %d - %s\n"
                                 % (h, d, self.h["%d %02d" % (d, h)]))

    def to_gchart(self):
        from pygooglechart import ScatterChart
        chart = ScatterChart(800, 300, x_range=(-1, 24), y_range=(-1, 7))

        chart.add_data([(h % 24) for h in range(24 * 8)])

        d=[]
        for i in range(8):
            d.extend([i] * 24)
        chart.add_data(d)

        day_names = "Sun Mon Tue Wed Thu Fri Sat".split(" ")
        days = (0, 6, 5, 4, 3, 2, 1)

        sizes=[]
        for d in days:
            sizes.extend([self.h["%d %02d" % (d, h)] for h in range(24)])
        sizes.extend([0] * 24)
        chart.add_data(sizes)

        chart.set_axis_labels('x', [''] + [str(h) for h  in range(24)] + [''])
        chart.set_axis_labels('y', [''] + [day_names[n] for n in days] + [''])

        chart.add_marker(1, 1.0, 'o', '333333', 25)
        return chart.get_url() + '&chds=-1,24,-1,7,0,20'

class Contributors(object):

    width = 420
    height = 300
    max_entries = 6

    def __init__(self, log_args=['HEAD']):
        self.data=[]
        args = ['git', 'shortlog', '-sn'] + log_args
        sub = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)

        for l in sub.stdout:
            commits, name = [x.strip() for x in l.split("\t")]
            commits = int(commits)
            self.data.append((name, commits))

    def dump(self):
        sys.stderr.write(repr(self.data) + "\n")

    def mk_chart(self):
        from pygooglechart import PieChart2D
        chart = PieChart2D(self.width, self.height)

        data = self.data[:self.max_entries]
        if len(self.data) > len(data):
            remainder = sum(d[1] for d in self.data[self.max_entries:])
            data.append(('Other', remainder))

        chart.add_data([d[1] for d in data])
        chart.set_pie_labels([d[0].split()[0] for d in data])
        return chart

    def to_gchart(self):
        return self.mk_chart().get_url()

class ChangeOverTime(object):

    width = 800
    height = 300
    max_entries = 6

    def __init__(self, log_args=['HEAD']):
        self.newdata = []
        self.cumulative = []
        self.cmax = 0
        self.max = 0

    def add_logs(self, directory=None, log_args=['HEAD']):
        args = ['git', 'log', '--pretty=format:%at'] + log_args
        sub = subprocess.Popen(args, stdout=subprocess.PIPE, close_fds=True)

        dates = {}
        for l in sub.stdout:
            k = time.strftime("%F", time.localtime(float(l.strip())))
            dates[k] = dates.get(k, 0) + 1

        total = 0
        for k,v in sorted(dates.items()):
            total += v
            self.max = max(self.max, v)
            self.newdata.append( (k, v) )
            self.cumulative.append( (k, total) )

        self.cmax = total

    def dump(self):
        sys.stderr.write(repr(self.data) + "\n")

    def mk_chart(self):
        from pygooglechart import SimpleLineChart
        chart =  SimpleLineChart(self.width, self.height)

        all_labels = [d[0] for d in self.cumulative]

        chart.add_data([d[1] for d in self.cumulative])
        chart.set_axis_labels('y', range(0, self.cmax, (self.cmax / 4)))
        chart.set_axis_labels('x', [all_labels[x] for x in
                                    range(0, len(all_labels), (len(all_labels) / 4))])
        return chart

    def to_gchart(self):
        return self.mk_chart().get_url()

def open_chart(chartish):
    subprocess.check_call(['open', chartish.to_gchart()])
