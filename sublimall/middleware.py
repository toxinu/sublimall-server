# -*- coding: utf-8 -*-
import traceback
import sys


class ProcessExceptionMiddleware(object):
    def process_exception(self, request, exception):
        print(exception)
        print(''.join(traceback.format_exception(*sys.exc_info())))
