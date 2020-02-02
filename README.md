# Simulation of Heavy Rain in Berlin

Simulates the water mass flows in Berlin after strong precipitation. Uses exclusively data form the [Berlin Open Data Portal](https://daten.berlin.de).


## Thank You!

Many thanks to my fellow student and friend [chrisschroer](https://github.com/chrisschroer) for the offline discussions.


## Description

This project carried out as part of the Urban Technology course at the Beuth University of Applied Sciences in Berlin of the masters course Data Science. Please note this.

Please have a look at the [slides](./reports/slides.pdf) of the internal given presentation. A simulation of the rainfalls in 2017 are [here available](https://github.com/se-jaeger/urban-technologies-berlin/blob/master/data/interim/simulation/berlin_17.gif).


## Data and Data Licence

This repository contains two datasets, and variants thereof, of the [Berlin Open Data Portal](https://daten.berlin.de) and one combining both.

The data can be found in the directory: [data/preprocessed](data/preprocessed)


### Dataset: Versiegelung 2016 (Ausgabe 2017)

Nutzungsbedingungen: Für die Nutzung der Daten ist die Datenlizenz Deutschland - Namensnennung - Version 2.0 anzuwenden. Die Lizenz ist über https://www.govdata.de/dl-de/by-2-0 abrufbar. Der Quellenvermerk gemäß (2) der Lizenz lautet "Umweltatlas Berlin / Versiegelung 2016 (Ausgabe 2017)"

**Original Data:** https://fbinter.stadt-berlin.de/fb/berlin/service_intern.jsp?id=sach_nutz2015_nutzsa@senstadt&type=WFS

**Changes:** The file format is `geojson` and columns are omitted


### Dataset: ATKIS® DGM − Digitales Geländemodell

Nutzungsbedingungen: Für die Nutzung der Daten ist die Datenlizenz Deutschland - Namensnennung - Version 2.0 anzuwenden. Die Lizenz ist über https://www.govdata.de/dl-de/by-2-0 abrufbar. Der Quellenvermerk gemäß (2) der Lizenz lautet "Umweltatlas Berlin / ATKIS® DGM − Digitales Geländemodell"

**Original Data:** https://fbinter.stadt-berlin.de/fb/berlin/service_intern.jsp?id=a_dgm@senstadt&type=FEED

Tool to download and create this data set is provided in https://github.com/se-jaeger/berlin-gelaendemodelle-downloader


### Dataset: Sealing and Ground Level of Berlin

Combines the two above mentioned datasets and is redistributed under the same licence.

Nutzungsbedingungen: Für die Nutzung der Daten ist die Datenlizenz Deutschland - Namensnennung - Version 2.0 anzuwenden. Die Lizenz ist über https://www.govdata.de/dl-de/by-2-0 abrufbar. Der Quellenvermerk gemäß (2) der Lizenz lautet "Umweltatlas Berlin / ATKIS® DGM − Sealing and Ground Level of Berlin"




## Information about the Scaffold

### Installation

In order to set up the necessary environment:

1. create an environment `urban-technologies-berlin` with the help of [conda],
   ```
   conda env create -f environment.yaml
   ```
2. activate the new environment with
   ```
   conda activate urban-technologies-berlin
   ```
3. install `urban-technologies-berlin` with:
   ```
   python setup.py install # or `develop`
   ```

Optional and needed only once after `git clone`:

4. install several [pre-commit] git hooks with:
   ```
   pre-commit install
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

5. install [nbstripout] git hooks to remove the output cells of committed notebooks with:
   ```
   nbstripout --install --attributes notebooks/.gitattributes
   ```
   This is useful to avoid large diffs due to plots in your notebooks.
   A simple `nbstripout --uninstall` will revert these changes.

Then take a look into the `scripts` and `notebooks` folders.


### Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yaml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yaml` for the exact reproduction of your
   environment with:
   ```
   conda env export -n urban-technologies-berlin -f environment.lock.yaml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yaml` using:
   ```
   conda env update -f environment.lock.yaml --prune
   ```


### Project Organization

```
├── AUTHORS.rst             <- List of developers and maintainers.
├── CHANGELOG.rst           <- Changelog to keep track of new features and fixes.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yaml        <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- Use `python setup.py develop` to install for development or
|                              or create a distribution with `python setup.py bdist_wheel`.
├── src
│   └── dsproject_demo      <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `py.test`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```


## Note

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
