"""Test that we can debug inferiors that handle SIGSEGV by themselves"""

from __future__ import print_function

import lldb_shared

import os
import lldb
from lldbtest import *
import lldbutil
import re


class HandleSegvTestCase(TestBase):

    mydir = TestBase.compute_mydir(__file__)

    @skipIfWindows # signals do not exist on Windows
    @skipIfDarwin
    @expectedFailureFreeBSD("llvm.org/pr23699 SIGSEGV is reported as exception, not signal")
    def test_inferior_handle_sigsegv(self):
        self.build()
        exe = os.path.join(os.getcwd(), "a.out")

        # Create a target by the debugger.
        target = self.dbg.CreateTarget(exe)
        self.assertTrue(target, VALID_TARGET)

        # launch
        process = target.LaunchSimple(None, None, self.get_process_working_directory())
        self.assertTrue(process, PROCESS_IS_VALID)
        self.assertEqual(process.GetState(), lldb.eStateStopped)
        signo = process.GetUnixSignals().GetSignalNumberFromName("SIGSEGV")

        thread = lldbutil.get_stopped_thread(process, lldb.eStopReasonSignal)
        self.assertTrue(thread and thread.IsValid(), "Thread should be stopped due to a signal")
        self.assertTrue(thread.GetStopReasonDataCount() >= 1, "There was data in the event.")
        self.assertEqual(thread.GetStopReasonDataAtIndex(0), signo, "The stop signal was SIGSEGV")

        # Continue until we exit.
        process.Continue()
        self.assertEqual(process.GetState(), lldb.eStateExited)
        self.assertEqual(process.GetExitStatus(), 0)
