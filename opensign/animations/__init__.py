# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""Animation plugin discovery, base class, and dispatcher."""

import os
from abc import ABC


class Animation(ABC):
    """Base class for animation plugins."""

    def __init__(self, sign):
        self._sign = sign

    @property
    def width(self):
        """Return the sign width."""
        return self._sign.width

    @property
    def height(self):
        """Return the sign height."""
        return self._sign.height

    @property
    def position(self):
        """Return the current sign position."""
        return self._sign._position

    @position.setter
    def position(self, value):
        self._sign._position = value

    def centered_position(self, message):
        """Return the centered position for a message."""
        return self._sign._get_centered_position(message)

    def draw(self, message, x, y, opacity=1.0):
        """Draw a message to the sign."""
        self._sign._draw(message, x, y, opacity=opacity)

    def draw_image(
        self,
        image,
        x,
        y,
        opacity=1.0,
        shadow_intensity=0,
        shadow_offset=0,
    ):
        """Draw an image to the sign."""
        self._sign._draw_image(
            image,
            x,
            y,
            opacity,
            shadow_intensity,
            shadow_offset,
        )

    def draw_message_image(self, message, image, x, y):
        """Draw an image using a message's visual settings."""
        self.draw_image(
            image,
            x,
            y,
            message.opacity,
            message.shadow_intensity,
            message.shadow_offset,
        )

    def create_loop_image(self, image, x_offset, y_offset):
        """Create a loop image from a source image."""
        return self._sign._create_loop_image(image, x_offset, y_offset)

    def wait(self, start_time, duration):
        """Wait until duration has elapsed since start_time."""
        return self._sign._wait(start_time, duration)

    def wait_for_steps(self, start_time, duration, steps):
        """Wait for one step of a stepped animation."""
        if steps:
            return self.wait(start_time, duration / steps)
        return start_time


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


def animate(sign, message, class_name, method_name, **kwargs):
    """Dispatch an animation by plugin class and method name."""
    animation_class = _load_animation_class(class_name)
    animation = animation_class(sign)

    try:
        method = getattr(animation, method_name)
    except AttributeError as error:
        raise ValueError(f"Unknown {class_name} animation: {method_name}") from error

    return method(message, **kwargs)


Animations.load_animations()
