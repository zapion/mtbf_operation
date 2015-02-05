mtbf_operation
==============
To setup mtbf environment for lab testing.  It will help to pull dependencies, flashing and/or executing tests
Dependencies:
* MTBF-Driver
* combo-runner
* B2G-flash-tool (for flashing)
* lockfile (python library for file lock)

Recommend to use flame

Quick start:
1. Pull this repo
2. make vmaster
3. run "MTBF_CONF=mtbf_config.json mtbf_job_runner.py --testvars={TESTVARS}"


TODO:
* Integrating all tasks/action and run (done)
* All tasks can be run individually 
* Re-writing script to adapting new architecture
  * 7-mobile settings (done)
  * change memory size (done)
  * check resource (done)
  * environment cleanup - remove port forwarding (done)
  * memory nfs indep symbol - collect memory report (done) - force crash dump (deprecated)
  * common check gaia (done)
  * common check B2G flash tool (done)
  * virtualenv setup (done)
  * port detection (done)
  * prerun (done)
  * run mtbf multi new
  * shallow flash indep symbol
