# SPDX-FileCopyrightText: 2020 Melissa LeBlanc-Williams
#
# SPDX-License-Identifier: MIT

"""YAML script runner for PyOpenSign."""

import argparse
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from . import DEFAULT, OpenSign

PATH_KEYS = {"file", "image", "font_file", "background_image"}


def _resolve_path(base_path, value):
    if not isinstance(value, str):
        return value

    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return base_path / path


def _resolve_paths(base_path, values):
    return {
        key: _resolve_path(base_path, value) if key in PATH_KEYS else value
        for key, value in values.items()
    }


def _as_mapping(value, action):
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{action} expects a mapping.")
    return dict(value)


def _as_list(value, action):
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return list(value)
    raise ValueError(f"{action} expects a list.")


def _parse_step(step):
    if isinstance(step, str):
        return step, None
    if not isinstance(step, Mapping) or len(step) != 1:
        raise ValueError("Each script step must be a command string or a single-key mapping.")
    return next(iter(step.items()))


class ScriptRunner:
    """Run a PyOpenSign YAML script."""

    def __init__(self, script_file):
        self.script_file = Path(script_file).expanduser().resolve()
        self.base_path = self.script_file.parent
        self.script = self._load_script()
        self.sign = self._create_sign()
        self._configure()

    def _load_script(self):
        with open(self.script_file) as script:
            loaded = yaml.safe_load(script) or {}
        if not isinstance(loaded, Mapping):
            raise ValueError("The script root must be a mapping.")
        return dict(loaded)

    def _create_sign(self):
        sign_config = dict(self.script.get("sign", {}))
        sign_config.pop("background_color", None)
        sign_config.pop("background_image", None)
        return OpenSign(**sign_config)

    def _configure(self):
        self._configure_sign_background()
        self._configure_fonts()
        self._configure_canvases()

    def _configure_sign_background(self):
        sign_config = self.script.get("sign", {})
        if "background_color" in sign_config:
            self.sign.set_background_color(sign_config["background_color"])
        if "background_image" in sign_config:
            self.sign.set_background_image(
                _resolve_path(self.base_path, sign_config["background_image"])
            )

    def _configure_fonts(self):
        fonts = self.script.get("fonts", {})
        if isinstance(fonts, Mapping):
            fonts = [{"name": name, **config} for name, config in fonts.items()]

        for font in fonts:
            config = _resolve_paths(self.base_path, _as_mapping(font, "font"))
            self.sign.add_font(config["name"], config["file"], config.get("size"))

    def _configure_canvases(self):
        canvases = self.script.get("canvases", {})
        if isinstance(canvases, Mapping):
            canvases = [{"name": name, **(config or {})} for name, config in canvases.items()]

        for canvas in canvases:
            config = _resolve_paths(self.base_path, _as_mapping(canvas, "canvas"))
            name = config.pop("name")
            if name == DEFAULT:
                self._set_canvas_properties(self.sign.get_canvas(DEFAULT), config)
            else:
                self.sign.create_canvas(name, **config)

    def _set_canvas_properties(self, canvas, config):
        for key, value in config.items():
            resolved_value = value
            if key == "position" and isinstance(value, str):
                resolved_value = self._canvas(value).position
            setattr(canvas, key, resolved_value)

    def _canvas(self, name=None):
        return self.sign.get_canvas(DEFAULT if name is None else name)

    def _command_sleep(self, params):
        time.sleep(params if params is not None else 0)

    def _command_add_font(self, params):
        config = _resolve_paths(self.base_path, _as_mapping(params, "add_font"))
        self.sign.add_font(config["name"], config["file"], config.get("size"))

    def _command_create_canvas(self, params):
        if isinstance(params, str):
            params = {"name": params}
        config = _resolve_paths(self.base_path, _as_mapping(params, "create_canvas"))
        name = config.pop("name")
        self.sign.create_canvas(name, **config)

    def _command_remove_canvas(self, params):
        self.sign.remove_canvas(params)

    def _command_set_background_color(self, params):
        self.sign.set_background_color(params)

    def _command_set_background_image(self, params):
        self.sign.set_background_image(_resolve_path(self.base_path, params))

    def _command_set_canvas(self, params):
        config = _as_mapping(params, "set_canvas")
        canvas = self._canvas(config.pop("canvas", None))
        self._set_canvas_properties(canvas, config)

    def _command_add_text(self, params):
        config = _resolve_paths(self.base_path, _as_mapping(params, "add_text"))
        canvas = config.pop("canvas", None)
        text = config.pop("text")
        self._canvas(canvas).add_text(text, **config)

    def _command_add_image(self, params):
        if isinstance(params, str):
            params = {"file": params}
        config = _resolve_paths(self.base_path, _as_mapping(params, "add_image"))
        canvas = config.pop("canvas", None)
        self._canvas(canvas).add_image(config["file"])

    def _command_clear(self, params):
        if isinstance(params, Mapping):
            canvas = params.get("canvas")
        else:
            canvas = params
        self._canvas(canvas).clear()

    def _command_draw_canvases(self, params):
        self.sign.draw_canvases(*_as_list(params, "draw_canvases"))

    def _command_animate(self, params):
        config = _as_mapping(params, "animate")
        animation = config.pop("name", None)
        if animation is None:
            class_name = config.pop("class")
            method_name = config.pop("method")
            animation = f"{class_name}.{method_name}"
        self.sign.animate(animation, **config)

    def _command_repeat(self, params):
        config = _as_mapping(params, "repeat")
        steps = _as_list(config.get("steps"), "repeat steps")
        count = config.get("count", 1)
        if count in {True, "forever"}:
            while True:
                self.run_steps(steps)
        for _ in range(count):
            self.run_steps(steps)

    def run_command(self, action, params=None):
        """Run one script command."""
        if action in {"sleep", "wait"}:
            self._command_sleep(params)
        elif action == "add_font":
            self._command_add_font(params)
        elif action == "create_canvas":
            self._command_create_canvas(params)
        elif action == "remove_canvas":
            self._command_remove_canvas(params)
        elif action == "set_background_color":
            self._command_set_background_color(params)
        elif action == "set_background_image":
            self._command_set_background_image(params)
        elif action == "set_canvas":
            self._command_set_canvas(params)
        elif action == "add_text":
            self._command_add_text(params)
        elif action == "add_image":
            self._command_add_image(params)
        elif action == "clear":
            self._command_clear(params)
        elif action in {"draw_canvases", "draw"}:
            self._command_draw_canvases(params)
        elif action == "animate":
            self._command_animate(params)
        elif action == "repeat":
            self._command_repeat(params)
        elif "." in action:
            self.sign.animate(action, **_as_mapping(params, action))
        elif callable(getattr(self.sign, action, None)):
            getattr(self.sign, action)(**_as_mapping(params, action))
        else:
            raise ValueError(f"Unknown script command: {action}")

    def run_steps(self, steps):
        """Run a list of script steps once."""
        for step in steps:
            action, params = _parse_step(step)
            self.run_command(action, params)

    def run(self):
        """Run the script."""
        steps = _as_list(self.script.get("steps"), "steps")
        repeat = self.script.get("repeat", False)

        if repeat in {True, "forever"}:
            while True:
                self.run_steps(steps)

        repeat_count = repeat if isinstance(repeat, int) and repeat is not False else 1
        for _ in range(repeat_count):
            self.run_steps(steps)


def run_script(script_file):
    """Run a PyOpenSign YAML script file."""
    ScriptRunner(script_file).run()


def main(argv=None):
    """Run the osscript command."""
    parser = argparse.ArgumentParser(description="Run a PyOpenSign YAML script.")
    parser.add_argument("script", help="Path to the YAML script file.")
    args = parser.parse_args(argv)
    run_script(args.script)


if __name__ == "__main__":
    main()
