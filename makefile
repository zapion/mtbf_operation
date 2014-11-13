# Pull all dependencies for mtbf runner
#

branch = v2.1
mtbf-env = mtbf-env

all: combo-runner mtbf-v2.1 virtual-env activate

virtual-env:
	virtualenv ${mtbf-env}

activate: mtbf-driver
	@. ${mtbf-env}/bin/activate; cd MTBF-Driver; \
	python setup.py install;

mtbf-v2.1: mtbf-driver
	@cd MTBF-Driver && git checkout v2.1;

combo-runner:
	@git clone https://github.com/Mozilla-TWQA/combo-runner.git;

mtbf-driver:
	@git clone https://github.com/Mozilla-TWQA/MTBF-Driver.git;

run:

clean:
	@rm -rf MTBF-Driver; rm -rf combo-runner; rm -rf ${mtbf-env}
