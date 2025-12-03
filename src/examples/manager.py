from ditl.transformation import manager

import examples.transformations.youtube

# print(manager._registered_transformations)
result = manager._registered_transformations["youtube_channel_overview"].execute(
)
print(result.data_frame)
manager._registered_transformations["youtube_channel_overview"].save_output_table(
    result=result
)
