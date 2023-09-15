from evo.world import World

from abc import ABC


class Callback(ABC):

    def __init__(self, config: dict, callback_name: str) -> None:
        self.global_config = config
        callbacks_config = config.get('callbacks')
        self.config = callbacks_config.get(callback_name)
        self.priority = self.config.get('priority', 0)

    def on_step_finish(self, generation: int, world: World) -> dict:
        return dict()

    def on_generation_finish(self,
                             generation: int,
                             generation_logs: dict,
                             world: World) -> None:
        pass

    def on_interrupt(self, world: World) -> None:
        pass


class RunCallbacks(Callback):

    def __init__(self, callbacks=None):
        self.callbacks = callbacks or []
        self.callbacks = sorted(self.callbacks, key=lambda cb: cb.priority)

    def add_callback(self, callback):
        self.callbacks.append(callback)
        self.callbacks = sorted(self.callbacks, key=lambda cb: cb.priority)

    def on_step_finish(self, generation: int, world: World) -> dict:
        logs = {}
        for callback in self.callbacks:
            logs.update(callback.on_step_finish(generation, world))
        return logs

    def on_generation_finish(self,
                             generation: int,
                             generation_logs: dict,
                             world: World) -> None:
        for callback in self.callbacks:
            callback.on_generation_finish(generation, generation_logs, world)

    def on_interrupt(self, world: World) -> None:
        for callback in self.callbacks:
            callback.on_interrupt(world)
