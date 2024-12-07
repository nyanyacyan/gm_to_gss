#  coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------


import asyncio
import time
from method.base.utils import Logger
from method.flow import Flow



# ------------------------------------------------------------------------------
# **********************************************************************************


class Main:
    def __init__(self, debugMode=True):

        # logger
        self.getLogger = Logger(__name__, debugMode=debugMode)
        self.logger = self.getLogger.getLogger()

        self.flow = Flow(debugMode=debugMode)


# ----------------------------------------------------------------------------------


    async def run_flow(self):
        start_time = time.time()

        await self.flow.process()

        end_time = time.time()
        return end_time - start_time


# ----------------------------------------------------------------------------------


if __name__ == '__main__':
    main = Main()
    asyncio.run(main.run_flow())



# ----------------------------------------------------------------------------------
# **********************************************************************************




