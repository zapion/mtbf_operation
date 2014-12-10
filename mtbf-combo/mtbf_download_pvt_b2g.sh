#!/bin/bash
## TODO:
##  1. Choose build? Apply B2G-flash-tool?
##  2. JENKINSQA_PWD handling

### Start MTBF pvt b2g build download process
echo "### MTBF PVT B2G DOWNLOAD SCRIPT"

### Download code: Gaia & Gecko
wget --http-user=jenkinsqa --http-passwd=${JENKINSQA_PWD} --progress=bar https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly/${BRANCH}/latest/${GAIA}
wget --http-user=jenkinsqa --http-passwd=${JENKINSQA_PWD} --progress=bar https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly/${BRANCH}/latest/${GECKO}

### Download debugging symbols:
wget --http-user=jenkinsqa --http-passwd=${JENKINSQA_PWD} --progress=bar https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly/${BRANCH}/latest/${SYMBOLS}

### Download sources.xml
wget --http-user=jenkinsqa --http-passwd=${JENKINSQA_PWD} --progress=bar https://pvtbuilds.mozilla.org/pvt/mozilla.org/b2gotoro/nightly/${BRANCH}/latest/sources.xml

### Create directory and move files
BUILD_DIR=build$(($(date +%s%N)/1000000))
mkdir ${BUILD_DIR}
mv ${GAIA}     ${BUILD_DIR}/gaia.zip
mv ${GECKO}    ${BUILD_DIR}/b2g.tar.gz
mv ${SYMBOLS}  ${BUILD_DIR}/symbols.zip
mv sources.xml ${BUILD_DIR}/sources.xml

### Export variables for others to use
export B2G_BUILD_DIR=${BUILD_DIR}

### SCRIPT Pre-TEST End with return code 99
exit 99
