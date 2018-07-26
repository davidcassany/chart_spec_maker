# chart_spec_maker

This is a simple python script to parse the index yaml file of kubernetes
helm chart repository and create a spec file for each entry.

The resulting spec can be used to create an RPM containing all the charts
listed in each entry.
