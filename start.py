from scrapy.cmdline import execute
import sys

path = sys.argv[:2]
for argv in sys.argv[2:]:
    args = path + [argv]
    execute(args)
