from typing import Type

# import evo.util.callback as callback
# import evo.repop.repop_fn as repop_fn
# import evo.selection.selection_fn as selection_fn
# import evo.world_gen.world_generator as world_generator


SELECT = 'selection_fn'
REPOP = 'repopulation_fn'
CALLBACK = 'callback'
WORLD_GEN = 'world_generator'

_registry = {
    SELECT: {},
    REPOP: {},
    CALLBACK: {},
    WORLD_GEN: {},
}


def register_callback_class(name: str, cb_cls: Type['callback.Callback']):
    _registry[CALLBACK][name] = cb_cls


def register_selection_fn_class(name: str, selection_cls: Type['selection_fn.SelectionFunction']):
    _registry[SELECT][name] = selection_cls


def register_repop_fn_class(name: str, repop_cls: Type['repop_fn.RepopFunction']):
    _registry[REPOP][name] = repop_cls


def register_world_gen_class(name: str, world_gen_cls: Type['world_generator.WorldGenerator']):
    _registry[WORLD_GEN][name] = world_gen_cls


def register_repop_fn(name: str):
    def decorator(repop_cls: Type['repop_fn.RepopFunction']):
        register_repop_fn_class(name, repop_cls)
        return repop_cls
    return decorator


def register_selection_fn(name: str):
    def decorator(selection_cls: Type['selection_fn.SelectionFunction']):
        register_selection_fn_class(name, selection_cls)
        return selection_cls
    return decorator


def register_callback(name: str):
    def decorator(cb_cls: Type['callback.Callback']):
        register_callback_class(name, cb_cls)
        return cb_cls
    return decorator


def register_world_gen(name: str):
    def decorator(world_gen_cls: Type['world_generator.WorldGenerator']):
        register_world_gen_class(name, world_gen_cls)
        return world_gen_cls
    return decorator


def _get_from_registry(registry_name: str, config: dict, registered_cls_name: str) -> object:

    if registry_name not in _registry:
        raise ValueError(f'No {registry_name} registry')

    cls = _registry[registry_name].get(registered_cls_name)
    if cls is None:
        raise Exception(f'No {registry_name} registered for {registered_cls_name}')

    return cls(config, registered_cls_name)


def get_selection_function(config: dict) -> 'selection_fn.SelectionFunction':
    selection_config = config.get('selection_config')
    if selection_config is None:
        raise Exception('selection_config not specified in config')

    selection_method = selection_config.get('method')
    if selection_method is None:
        raise Exception('selection_method not specified in config: ' + str(selection_config))

    return _get_from_registry(SELECT, config, selection_method)


def get_repop_function(config: dict) -> 'repop_fn.RepopFunction':
    repop_config = config.get('repop_config')
    if repop_config is None:
        raise Exception('repopulation_config not specified in config')

    repop_method = repop_config.get('method')
    if repop_method is None:
        raise Exception('repopulation_method not specified in config: ' + str(repop_config))

    return _get_from_registry(REPOP, config, repop_method)


def get_callback(config: dict, callback_name: str) -> 'callback.Callback':
    return _get_from_registry(CALLBACK, config, callback_name)


def get_world_generator(config: dict) -> 'world_generator.WorldGenerator':
    world_gen_config = config.get('world_gen')
    if world_gen_config is None:
        return _get_from_registry(WORLD_GEN, config, 'no_gen')

    world_gen_method = world_gen_config.get('method')
    if world_gen_method is None:
        raise Exception('world_gen_method not specified in config: ' + str(world_gen_config))

    return _get_from_registry(WORLD_GEN, config, world_gen_method)
