# import pandas as pd
# from ditl_engine_pandas.functions.join import PandasJoinArgSpec

# from ditl.models.data_frame_wrapper.preloaded_wrapper import DataFrameWrapper, TypedDataFrameWrapper
# from ditl.transformation import manager
# from ditl_pandas_example.models.youtube import (
#     tech_channel_overview,
#     tech_channel_overview_2,
#     tech_channel_overview_3,
#     tech_channels,
#     tech_videos,
# )


# @manager.register_transformation(
#     output_table_model=tech_channel_overview,
#     tech_videos=tech_videos,
#     tech_channels=tech_channels,
# )
# def youtube_channel_overview(
#     tech_videos: TypedDataFrameWrapper[pd.DataFrame], tech_channels: TypedDataFrameWrapper[pd.DataFrame]
# ):
#     tech_channel_overview = tech_channels.join(
#         function_spec=PandasJoinArgSpec(other=tech_videos, left_on=["channel_id"], right_on=["channel_id"], how="left")
#     )
#     print("yeah")
#     tech_channel_overview = DataFrameWrapper(
#         data_frame=tech_channel_overview.data_frame.groupby("channel_id").agg(
#             pd.sum("views").alias("channel_views"),
#             pd.sum("likes").alias("channel_likes"),
#         )
#     )
#     tech_channel_overview = tech_channel_overview.join(
#         PandasJoinArgSpec(
#             other=tech_channels.data_frame.select(["channel_id", "channel_name"]),
#             left_on=["channel_id"],
#             right_on=["channel_id"],
#             how="inner",
#         )
#     )
#     return tech_channel_overview


# # @manager.register_transformation(
# #     output_table_model=tech_channel_overview,
# #     tech_videos=tech_videos,
# #     tech_channels=tech_channels,
# # )
# # def youtube_channel_overview_failing(tech_videos: DataFrameWrapper, tech_channels: DataFrameWrapper):
# #     tech_channel_overview = tech_channels.data_frame.join(tech_videos.data_frame, on="channel_id", how="left")
# #     tech_channel_overview = (
# #         tech_channel_overview.group_by("channel_id")
# #         .agg(
# #             pl.sum("views").alias("channel_views"),
# #             pl.sum("likes").alias("channel_likes"),
# #         )
# #         .join(
# #             tech_channels.data_frame.select(["channel_id", "channel_name"]),
# #             on="channel_id",
# #             how="inner",
# #         )
# #         .select("channel_views", "foo")
# #     )
# #     return tech_channel_overview


# @manager.register_transformation(
#     output_table_model=tech_channel_overview_2,
#     tech_videos=tech_videos,
#     tech_channel_overview=tech_channel_overview,
# )
# def youtube_channel_overview_2(tech_videos: DataFrameWrapper, tech_channel_overview: DataFrameWrapper):
#     return tech_channel_overview


# @manager.register_transformation(
#     output_table_model=tech_channel_overview_3,
#     tech_videos=tech_videos,
# )
# def youtube_channel_overview_3(tech_videos: DataFrameWrapper):
#     return tech_videos
