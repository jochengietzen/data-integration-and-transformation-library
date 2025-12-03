from ditl.transformation import manager


# print(manager._registered_transformations)
result = manager._registered_transformations["youtube_channel_overview"].execute()
print(result.data_frame)
manager._registered_transformations["youtube_channel_overview"].save_output_table(
    result=result
)

# TODO: Next step: Work on fake data generation
# TODO: Next step: TablePath Abhängigkeit von Environment/Config
# TODO: Discuss if name should be part of path or table itself
