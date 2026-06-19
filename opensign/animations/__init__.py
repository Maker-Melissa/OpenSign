# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Animation plugin discovery and dispatcher."""

import os


class Animations:
    """Class that automatically loads animation plugins from this package."""

    _valid_animations = []

    @staticmethod
    def load_animations():
        """Load available animation module names and set them as attributes."""
        animation_folder = __file__.split("/")[0:-1]
        animation_folder = "/".join(animation_folder)
        animations = sorted(os.listdir(animation_folder))
        Animations._valid_animations = [
            animation.split(".")[0]
            for animation in animations
            if animation.endswith(".py")
            and not animation.startswith("_")
            and animation != "__init__.py"
        ]
        for animation in Animations._valid_animations:
            setattr(Animations, animation.upper(), animation)

    @staticmethod
    def valid_animations():
        """Return the available animation plugin names."""
        return Animations._valid_animations


def _case_insensitive_find(items, name):
    for item in items:
        if item.lower() == name.lower():
            return item
    return None


def _load_animation_class(class_name):
    module_name = _case_insensitive_find(Animations.valid_animations(), class_name)
    if module_name is None:
        raise ValueError(
            "Invalid animation class. "
            "Use Animations.valid_animations() to get a list of valid animations."
        )

    parent_class = __name__.split(".")[0]
    class_path = (parent_class, "animations", module_name.lower())

    animation_class = __import__(".".join(class_path))
    for item in class_path[1:]:
        animation_class = getattr(animation_class, item)

    class_name = _case_insensitive_find(dir(animation_class), class_name)
    if class_name is None:
        raise ValueError(f"Animation class not found in {module_name}.py.")

    return getattr(animation_class, class_name)


def animate(sign, target, class_name, method_name, **kwargs):
    """Dispatch an animation by plugin class and method name."""
    animation_class = _load_animation_class(class_name)

    try:
        method = getattr(animation_class, method_name)
    except AttributeError as error:
        raise ValueError(f"Unknown {class_name} animation: {method_name}") from error

    return method(sign, target, **kwargs)


Animations.load_animations()
