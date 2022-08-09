build-bundle-rego:
	@mkdir -p bundles/
	@rm -f bundles/bundle.tar.gz
	@opa build --bundle policies/ --output bundles/bundle.tar.gz

edgedb-init:
	# in current, edgedb docker image not supports linux/arm64
	@mkdir -p ./edgedb/database/
	@mkdir -p ./edgedb/config/
	@docker run --name edgedb \
		-e EDGEDB_SERVER_TLS_CERT_MODE="generate_self_signed" \
		-e EDGEDB_SERVER_USER=${EDGEDB_SERVER_USER} \
	  	-e EDGEDB_SERVER_PASSWORD=${EDGEDB_SERVER_PASSWORD} \
	  	-v ${CURDIR}/edgedb/project/dbschema:/dbschema \
	  	-v ${CURDIR}/edgedb/database:/var/lib/edgedb/data \
	  	-v ${CURDIR}/edgedb/config:/.config/edgedb \
	  	-p 5656:5656 \
	  	--platform linux/amd64 \
	  	-d edgedb/edgedb

run-local: build-bundle-rego
	@docker-compose -f ./docker-compose.yml up
