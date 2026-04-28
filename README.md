# Data Integration and Transformation Library (DITL)
DITL is a library, that allows you to streamline your etl development process.

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
    - TODO: How should we handle DataType registration, when not yet present in ArrowEngine?
    - TODO: Revisit topic of preloaded DataFrameWrapper vs. manual load or separate module.
    - TODO: Try to make it work with complex types (Array, Map, Variant)
    - TODO: Provide testable function, so users can verify the wrapper functions in different engines provide the same results
