from ditl.models.base import DataFrameWrapper
from ditl.transformation import manager
from examples.models.youtube import tech_channel_overview, tech_channels, tech_videos
import polars as pl


@manager.register_transformation(
    output_table_model=tech_channel_overview,
    tech_videos=tech_videos,
    tech_channels=tech_channels,
)
def youtube_channel_overview(
    tech_videos: DataFrameWrapper, tech_channels: DataFrameWrapper
):
    tech_channel_overview = tech_channels.data_frame.join(
        tech_videos.data_frame, on="channel_id", how="left"
    )
    tech_channel_overview = (
        tech_channel_overview.group_by("channel_id")
        .agg(
            pl.sum("views").alias("channel_views"),
            pl.sum("likes").alias("channel_likes"),
        )
        .join(
            tech_channels.data_frame.select(["channel_id", "channel_name"]),
            on="channel_id",
            how="inner",
        )
    )
    return tech_channel_overview
