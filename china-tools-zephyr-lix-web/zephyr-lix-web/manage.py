#!/usr/bin/env python

from linkedin.web.devel import Manager


manager = Manager('zephyrlixweb.webapp:app', next_gen_cfg2_configs=True)


if __name__ == '__main__':
    manager.run()
