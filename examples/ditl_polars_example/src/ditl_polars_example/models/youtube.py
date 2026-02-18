from typing import Any

from ditl.config import EnvironmentConfig, RuntimeConfig
from ditl.engines.polars_engine import PolarsEngine
from ditl.models.base import (
    Column,
    Columns,
    EngineFileType,
    IntegerType,
    StringType,
    TablePath,
)
from ditl.models.data_frame_wrapper import DataFrameWrapper
from ditl.models.generation import Generation
from ditl.models.table import EngineReadSettings, EngineWriteSettings, Table
from ditl.testing.faker_type import FakerIntType, FakerStringType
from ditl_polars_example.config import MyEnvironmentConfig


class YoutubeTablePath(TablePath):
    date: str
    time: str
    name: str

    def full_path(
        self,
        *args: Any,
        runtime_config: RuntimeConfig,
        environment_config: MyEnvironmentConfig,
        **kwargs: dict[str, Any],
    ) -> str:
        return f"/workspace/data/{environment_config.env}/{self.name}_{self.date}_{self.time}.csv"


class YoutubeTable(Table):
    path: YoutubeTablePath
    engine_read_settings: EngineReadSettings = EngineReadSettings(
        engine=PolarsEngine,
        read_type=EngineFileType.CSV,
    )
    engine_write_settings: EngineWriteSettings = EngineWriteSettings(
        engine=PolarsEngine,
        write_type=EngineFileType.CSV,
    )

    def read(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        **kwargs,
    ) -> DataFrameWrapper:
        return super().read(
            *args,
            runtime_config=runtime_config,
            environment_config=environment_config,
            source=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
            **kwargs,
        )

    def write(
        self,
        *args,
        runtime_config: RuntimeConfig,
        environment_config: EnvironmentConfig,
        data_frame_wrapper: DataFrameWrapper,
        **kwargs,
    ) -> "YoutubeTable":
        return super().write(
            *args,
            runtime_config=runtime_config,
            environment_config=environment_config,
            data_frame_wrapper=data_frame_wrapper,
            file=self.path.full_path(runtime_config=runtime_config, environment_config=environment_config),
            **kwargs,
        )


class ReadTable(YoutubeTable):
    pass


tech_channels = ReadTable(
    path=YoutubeTablePath(
        name="youtube_tech_channels",
        date="20251120",
        time="133753",
    ),
    columns=Columns(
        root=dict(
            channel_id=Column(
                name="channel_id",
                data_type=StringType(),
                is_primary_key=True,
                generation=Generation(faker_type=FakerStringType()),
            ),
            channel_name=Column(
                name="channel_name",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            description=Column(
                name="description",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            subscribers=Column(
                name="subscribers",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            total_views=Column(
                name="total_views",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            total_videos=Column(
                name="total_videos",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            created_date=Column(
                name="created_date",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            country=Column(
                name="country",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            scraped_at=Column(
                name="scraped_at",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
        )
    ),
    description="Youtube tech channels",
)


tech_videos = YoutubeTable(
    path=YoutubeTablePath(
        name="youtube_tech_videos",
        date="20251120",
        time="133004",
    ),
    columns=Columns(
        root=dict(
            video_id=Column(
                name="video_id",
                data_type=StringType(),
                is_primary_key=True,
                generation=Generation(faker_type=FakerStringType()),
            ),
            title=Column(
                name="title",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            published_at=Column(
                name="published_at",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            views=Column(
                name="views",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=10, max_val=100)),
            ),
            likes=Column(
                name="likes",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
            comments=Column(
                name="comments",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
            duration=Column(
                name="duration",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            thumbnail=Column(
                name="thumbnail",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            video_url=Column(
                name="video_url",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            channel_id=Column(
                name="channel_id",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            channel_name=Column(
                name="channel_name",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
            scraped_at=Column(
                name="scraped_at",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
            ),
        )
    ),
    description="Youtube tech videos",
)

tech_channel_overview_3 = tech_videos.model_copy()
tech_channel_overview_3.path = YoutubeTablePath(name="youtube_channels_overview_3", date="1", time="2")

tech_channel_overview = YoutubeTable(
    path=YoutubeTablePath(name="youtube_channels_overview", date="1", time="2"),
    columns=Columns(
        root=dict(
            channel_id=Column(
                name="channel_id",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
                is_primary_key=True,
            ),
            channel_name=Column(
                name="channel_name", data_type=StringType(), generation=Generation(faker_type=FakerStringType())
            ),
            channel_views=Column(
                name="channel_views",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
            channel_duration=Column(
                name="channel_duration",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
        )
    ),
    description="Overview over the tech channels",
)

tech_channel_overview_2 = YoutubeTable(
    path=YoutubeTablePath(name="youtube_channels_overview_2", date="1", time="2"),
    columns=Columns(
        root=dict(
            channel_id=Column(
                name="channel_id",
                data_type=StringType(),
                generation=Generation(faker_type=FakerStringType()),
                is_primary_key=True,
            ),
            channel_name=Column(
                name="channel_name", data_type=StringType(), generation=Generation(faker_type=FakerStringType())
            ),
            channel_views=Column(
                name="channel_views",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
            channel_duration=Column(
                name="channel_duration",
                data_type=IntegerType(),
                generation=Generation(faker_type=FakerIntType(min_val=0, max_val=100)),
            ),
        )
    ),
    description="Overview over the tech channels",
)


if __name__ == "__main__":
    print(tech_channels.columns.get_schema())
    print(tech_videos.columns.get_schema())
    print(tech_channel_overview.columns.get_schema())
