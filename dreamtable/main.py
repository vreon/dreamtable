#!/usr/bin/env python

from pathlib import Path

from raylib.pyray import PyRay
import esper

from .constants import Tool, PositionSpace

from .components import (
    BackgroundGrid,
    Button,
    Camera,
    Canvas,
    DebugEntity,
    Deletable,
    Draggable,
    Extent,
    Hoverable,
    Image,
    Name,
    Position,
    PositionMarker,
    Pressable,
    Selectable,
    Theme,
    ToolSwitcher,
    WorldContext,
)
from .processors import (
    BackgroundGridRenderer,
    BoxSelectionController,
    BoxSelectionRenderer,
    ButtonRenderer,
    CameraContextController,
    CameraController,
    CanvasExportController,
    CanvasRenderer,
    DebugEntityRenderer,
    DragController,
    DropperToolController,
    DropperToolRenderer,
    EggTimerController,
    EggToolController,
    FinalDeleteController,
    GridToolController,
    GridToolRenderer,
    HoverController,
    ImageController,
    ImageDeleteController,
    MotionController,
    MouseController,
    PencilToolController,
    PencilToolRenderer,
    PositionMarkerRenderer,
    PressController,
    SelectableDeleteController,
    SpriteRegionRenderer,
    TinyFriendController,
    ToolSwitcherController,
    WanderingController,
)

pkg_path = Path(__file__).parent


################################################################################


def main():
    pyray = PyRay()

    # pyray.set_config_flags(pyray.FLAG_WINDOW_RESIZABLE)
    pyray.init_window(800, 600, "Dream Table")
    pyray.set_target_fps(60)

    world = esper.World()
    world.context = WorldContext(
        cameras={PositionSpace.SCREEN: pyray.Camera2D((0, 0), (0, 0), 0, 3)},
        theme=Theme(
            font=pyray.load_font(str(pkg_path / "resources/fonts/alpha_beta.png"))
        ),
    )

    # Spawn initial entities
    world.create_entity(
        Name("Camera"),
        Camera(active=True, camera_2d=pyray.Camera2D((0, 0), (0, 0), 0, 4)),
    )
    world.create_entity(Name("Origin"), Position(), PositionMarker())
    world.create_entity(
        Name("Minor grid"),
        BackgroundGrid(world.context.theme.color_grid_minor),
        Extent(8, 8),
    )
    world.create_entity(
        Name("Major grid"),
        BackgroundGrid(world.context.theme.color_grid_major),
        Extent(32, 32),
    )

    # debug: a draggable to drag around
    world.create_entity(
        Name("Draggable"),
        Position(214, 2, space=PositionSpace.SCREEN),
        Extent(50, 12),
        DebugEntity(),
        Hoverable(),
        Draggable(),
        Selectable(),
    )

    # debug: a canvas with a preloaded palette image
    world.create_entity(
        Name("Sweetie 16"),
        Canvas(),
        Position(),
        Extent(),
        Image(filename=str(pkg_path / "resources/palettes/sweetie-16-8x.png")),
        Draggable(),
        Hoverable(),
        Selectable(),
        Deletable(),
    )

    # debug: tool buttons
    world.create_entity(
        Name("Move"),
        Button(),
        ToolSwitcher(Tool.MOVE),
        Pressable(),
        Position(2 + 8 * 0, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/hand.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Pencil"),
        Button(),
        ToolSwitcher(Tool.PENCIL),
        Pressable(),
        Position(2 + 8 * 1, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/pencil.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Dropper"),
        Button(),
        ToolSwitcher(Tool.DROPPER),
        Pressable(),
        Position(2 + 8 * 2, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/dropper.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Grid"),
        Button(),
        ToolSwitcher(Tool.GRID),
        Pressable(),
        Position(2 + 8 * 3, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/grid.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Cellref"),
        Button(),
        ToolSwitcher(Tool.CELLREF),
        Pressable(),
        Position(2 + 8 * 4, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/cellref.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Cellref Dropper"),
        Button(),
        ToolSwitcher(Tool.CELLREF_DROPPER),
        Pressable(),
        Position(2 + 8 * 5, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/cellref_dropper.png")),
        Hoverable(),
    )
    world.create_entity(
        Name("Mystery Egg"),
        Button(),
        ToolSwitcher(Tool.EGG),
        Pressable(),
        Position(2 + 8 * 6, 2, space=PositionSpace.SCREEN),
        Extent(8, 8),
        Image(filename=str(pkg_path / "resources/icons/egg.png")),
        Hoverable(),
    )

    # Register controllers and renderers (flavors of processors)
    world.add_processor(CameraContextController())
    world.add_processor(MouseController())
    world.add_processor(PencilToolController())
    world.add_processor(DropperToolController())
    world.add_processor(GridToolController())
    world.add_processor(EggToolController())
    world.add_processor(DragController())
    world.add_processor(HoverController())
    world.add_processor(PressController())
    world.add_processor(BoxSelectionController())
    world.add_processor(ImageController())
    world.add_processor(ToolSwitcherController(pyray))
    world.add_processor(CanvasExportController())

    world.add_processor(CameraController())
    world.add_processor(MotionController())
    world.add_processor(WanderingController())
    world.add_processor(EggTimerController())
    world.add_processor(TinyFriendController())

    world.add_processor(BackgroundGridRenderer())
    world.add_processor(PositionMarkerRenderer())
    world.add_processor(CanvasRenderer())
    world.add_processor(SpriteRegionRenderer())
    world.add_processor(DebugEntityRenderer())
    world.add_processor(BoxSelectionRenderer())

    world.add_processor(ButtonRenderer())
    world.add_processor(DropperToolRenderer())
    world.add_processor(PencilToolRenderer())
    world.add_processor(GridToolRenderer())

    world.add_processor(SelectableDeleteController())
    world.add_processor(ImageDeleteController())
    world.add_processor(FinalDeleteController())

    while not pyray.window_should_close():
        pyray.begin_drawing()
        pyray.clear_background(world.context.theme.color_background)
        world.process(pyray)
        pyray.end_drawing()

    pyray.close_window()


if __name__ == "__main__":
    main()
