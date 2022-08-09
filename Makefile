build-bundle-rego:
	@mkdir -p bundles/
	@rm -f bundles/bundle.tar.gz
	@opa build --bundle policies/ --output bundles/bundle.tar.gz

run-local: build-bundle-rego
	@docker-compose -f ./docker-compose.yml up
