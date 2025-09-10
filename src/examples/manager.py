from ditl.transformation import manager
from examples.transformations import foo

print(manager._registered_transformations)
print(manager._registered_transformations["sample_transformation"].execute())
