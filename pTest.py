import dateutil.parser

a = {'iso': '2018-08-09T13:19:49.569Z', 'epoch': 1533820789.569}
print(dateutil.parser.parse('2018-08-09T13:19:49.569Z').timestamp())
print(a["iso"], a["epoch"])
