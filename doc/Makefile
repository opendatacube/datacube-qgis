# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXPROJ    = OpenDataCubeQGISPlugin
SOURCEDIR     = .
BUILDDIR      = ../datacube_query/help
SPHINXOPTS    = -d "$(SOURCEDIR)/build"
SPHINXBUILD   = sphinx-build

# Put it first so that "make" without argument is like "make html".
html:
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: html Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD)  -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)