check:
	pep8 image_view.py setup.py
	pylint \
		--reports=no \
		--disable=invalid-name \
		--rcfile=/dev/null \
		image_view.py setup.py
	check-manifest
	rstcheck --report=1 README.rst
	scspell image_view.py setup.py README.rst

readme:
	@restview --long-description --strict
