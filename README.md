# eltstar
eltstar is a library, that allows you to streamline your etl development process.

# Core features
- Simple generation of schemad valid fake data for local testing purposes
- Enabling easy data quality checks
- Providing Data Lineage within your package
- Streamlining deployment information for vaious platforms


# Naming
Wording is hard, and even though we know, that we will clash with some names of other libraries, like spark, we try to keep a consistant naming within the library!

### schema
The schema is used to define the structure of your data. It contains the name of each column as well as the type of each column. It is comparable to sparks schema of a table/dataframe etc.

# TODOS
    - TODO: How should we handle DataType registration, when not yet present in ArrowEngine? (V1)
    - TODO: Revisit topic of preloaded DataFrameWrapper vs. manual load or separate module. (V2)
    - TODO: Try to make it work with complex types (Array, Map, Variant) (V3?)
    - TODO: Provide testable function, so users can verify the wrapper functions in different engines provide the same results (V1)
    - TODO: Find a migration mechanism (V2/3)
            Current idea: define a migration table, that needs to be given a read/write method by the user. We can then track all model versions in that table and migrate the versions.
            Discuss how and when a version will be created.
            Should the table only track a state?
    - TODO: Embed example code into documentation (V1-2) to ensure example code is still valid/running. Also test and run all example code.
    - TODO: Test all examples automatically (through entrypoints?)
    - TODO: Finish CI Pipelines and finish Naming!

    - TODO: Generics in new style
    - TODO: Better Orchestration possibilities (stages etc.)

    - TODO: Commiting/Vetting Process
                - Maintainer only after vetting process/getting to know each other
                - Clear contribution rules (e.g. Size of PR if not [maintainer](https://carlos-camara.github.io/qa-hub-actions/actions/pr-size-labeler.html))
    - TODO: Streaming mode through implementation/protocol? for engine