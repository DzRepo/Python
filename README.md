# Python Utilities for working with Gnip APIs

#ProcessHistoricalPowerTrackJob.py -
Downloads, decompresses, and optionally processess individual activities within [Historical PowerTrack](http://support.gnip.com/apis/historical_api/) jobs.

  * Currently all settings are set in the script.  Need to add Command Line Parameter support.
  * Currently single-threaded.  Need to add multi-thread support as most of the time the script is I/O wait bound.