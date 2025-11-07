from ditl.transformation import manager

print(manager._registered_transformations)
print(manager._registered_transformations["sample_transformation"].execute())
