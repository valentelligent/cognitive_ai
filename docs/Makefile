# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
WATCHDIR      = ..

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean watch livehtml

# Custom clean command
clean:
	rm -rf $(BUILDDIR)/*
	rm -rf api_reference/

# Watch for file changes and rebuild
watch:
	@echo "Watching for file changes..."
	@watchmedo shell-command \
		--patterns="*.rst;*.md;*.py;*.txt" \
		--recursive \
		--command='$(MAKE) html' \
		$(WATCHDIR)

# Live reload documentation server
livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O) \
		--watch $(WATCHDIR) \
		--open-browser \
		--delay 2

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
