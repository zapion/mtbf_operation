# Pull all dependencies for mtbf runner
#

mtbf-env = mtbf-env
virtual-env-exists = $(shell if [ -d "mtbf-env" ]; then echo "exists"; fi)

setup-combo: combo-runner virtual-env activate

delete-mtbf-env:
	@rm -rf mtbf-env

v2.1: combo-runner mtbf-v2.1 virtual-env activate lib-install github-remove

vmaster: combo-runner mtbf-vmaster virtual-env activate lib-install github-remove

virtual-env:
ifneq ($(virtual-env-exists),exists)
	@virtualenv ${mtbf-env}
else
	@echo "virtual environment exists." 
endif

lib-install: virtual-env
	@. ${mtbf-env}/bin/activate; \
		pip install lockfile;

activate: mtbf-driver virtual-env
	@. ${mtbf-env}/bin/activate; \
		cd MTBF-Driver; \
	    python setup.py install; \
		cd ../combo-runner; \
		python setup.py install;

github-remove:
	@rm -rf MTBF-Driver combo-runner

mtbf-vmaster: mtbf-driver
	@cd MTBF-Driver && git checkout master;

mtbf-v2.1: mtbf-driver
	@cd MTBF-Driver && git checkout v2.1;

combo-runner:
	@git clone https://github.com/Mozilla-TWQA/combo-runner.git;

mtbf-driver:
	@git clone https://github.com/Mozilla-TWQA/MTBF-Driver.git;

update: 
	@cd MTBF-Driver; \
     git pull -u; \
     cd ../combo-runner; \
     git pull -u;

clean:
	@rm -rf MTBF-Driver; rm -rf combo-runner; rm -rf ${mtbf-env}
